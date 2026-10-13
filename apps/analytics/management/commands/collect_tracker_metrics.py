"""Poll TrackerRust /metrics/* and ingest presence/churn into Django."""
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone as dt_tz

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.analytics.models import AcademicDocument, ChurnEvent, PeerNode, SwarmSnapshot


def _get_json(url: str, timeout: int = 10) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class Command(BaseCommand):
    help = "Collect churn/presence from TrackerRust and update PeerNode / ChurnEvent"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tracker",
            default=os.environ.get("ALLIBRARY_TRACKER_URL", "http://127.0.0.1:8080"),
        )

    def handle(self, *args, **options):
        base = options["tracker"].rstrip("/")
        self.stdout.write(f"Polling {base} …")

        try:
            presence = _get_json(f"{base}/metrics/presence")
            churn = _get_json(f"{base}/metrics/churn")
            lobby = _get_json(f"{base}/lobby")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            self.stderr.write(self.style.ERROR(f"tracker unreachable: {exc}"))
            return

        online_ids = []
        for n in presence.get("nodes", []):
            nid = n.get("node_id")
            onion = n.get("onion") or f"{nid}.onion"
            try:
                import uuid

                uuid.UUID(str(nid))
            except Exception:
                continue
            online_ids.append(nid)
            PeerNode.objects.update_or_create(
                node_id=nid,
                defaults={
                    "onion_address": onion[:120],
                    "is_online": True,
                    "last_seen": timezone.now(),
                    "node_alias": str(nid)[:8],
                },
            )

        if online_ids:
            PeerNode.objects.exclude(node_id__in=online_ids).update(is_online=False)

        created = 0
        for ev in churn.get("events", []):
            et = ev.get("event_type") or "node_join"
            nid = str(ev.get("node_id") or "")[:80]
            at = ev.get("at")
            if isinstance(at, str) and at.isdigit():
                occurred = datetime.fromtimestamp(int(at), tz=dt_tz.utc)
            else:
                occurred = timezone.now()
            _, was_created = ChurnEvent.objects.get_or_create(
                event_type=et if et in ("node_join", "node_leave", "stale_evict") else "node_join",
                node_id=nid,
                occurred_at=occurred,
                defaults={"is_simulated": False},
            )
            if was_created:
                created += 1

        for f in lobby.get("files", []):
            ch = (f.get("content_hash") or "").lower()
            if not ch:
                continue
            name = (f.get("name") or "Lobby file")[:300]
            size = int(f.get("size") or 0)
            seeds = int(f.get("peer_count") or len(f.get("peers") or []))
            ext = name.rsplit(".", 1)[-1].upper() if "." in name else "PDF"
            file_type = ext if ext in ("PDF", "EPUB", "DOCX") else "PDF"
            chunk_size = 524288
            total_chunks = max(1, (size + chunk_size - 1) // chunk_size) if size else 1
            doc, _ = AcademicDocument.objects.update_or_create(
                content_hash=ch,
                defaults={
                    "title": name,
                    "author": "Rede P2P (lobby)",
                    "category": "COMPUTACAO",
                    "file_type": file_type,
                    "file_size_bytes": size,
                    "chunk_size_bytes": chunk_size,
                    "total_chunks": total_chunks,
                    "swarm_link": (f.get("swarm_link") or "")[:600],
                    "total_seeds_active": max(seeds, 1),
                },
            )
            health = "CRITICAL"
            if seeds >= 5:
                health = "EXCELLENT"
            elif seeds >= 2:
                health = "HEALTHY"
            elif seeds == 1:
                health = "DEGRADED"
            SwarmSnapshot.objects.create(
                document=doc,
                active_seeders=seeds,
                active_leechers=0,
                swarm_ratio=float(seeds) if seeds else 0.0,
                health_status=health,
                timestamp=timezone.now(),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"presence online={presence.get('online_nodes')} churn_new={created}"
            )
        )
