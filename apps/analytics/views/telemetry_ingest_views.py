from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.models import (
    AcademicDocument,
    TransferSession,
    ChunkPerformanceLog,
    LookupEvent,
    GossipPropagationEvent,
    ChurnEvent,
)
from apps.analytics.serializers.telemetry_ingest_serializer import (
    TransferIngestSerializer,
    ChunkIngestSerializer,
    LookupIngestSerializer,
    GossipIngestSerializer,
)


# Cap.6 / lobby — known academic documents (Tor-measured originals).
KNOWN_DOCUMENT_TITLES: dict[str, str] = {
    "472650b81a7b23d44c417a8625c6462d5e54b3b22b49b13e500d49a17c826e00": (
        "An_Historico_geographical_Description_of.pdf"
    ),
    "f27b5cb292a268fa70ef3cf211f2cbc2cb31d59eefa1b4053e74347f18bf91c4": (
        "Don Quixote - Miguel De Cervantes.pdf"
    ),
    "fa882d6974416da1319ac21569e3d76936575506aa875ce70abe28b7922c38b7": (
        "Fahrenheit 451 (Ray Bradbury) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
    ),
}


def _resolve_title(content_hash: str, file_name: str = "", document_title: str = "") -> str:
    ch = (content_hash or "").lower()
    for candidate in (document_title, file_name, KNOWN_DOCUMENT_TITLES.get(ch, "")):
        title = (candidate or "").strip()
        if title:
            return title[:255]
    return f"Measured transfer {ch[:12]}"


def _document_for_hash(
    content_hash: str,
    file_size: int,
    total_chunks: int,
    chunk_size: int,
    file_name: str = "",
    document_title: str = "",
) -> AcademicDocument:
    ch = content_hash.lower()
    title = _resolve_title(ch, file_name, document_title)
    existing = AcademicDocument.objects.filter(content_hash=ch).first()
    if existing:
        # Upgrade placeholder titles when a real name arrives.
        if existing.title.startswith("Measured transfer") and title and not title.startswith("Measured transfer"):
            AcademicDocument.objects.filter(pk=existing.pk).update(title=title)
            existing.title = title
        return existing
    return AcademicDocument.objects.create(
        title=title,
        author="anonymous",
        category='SEGURANCA',
        file_type='PDF',
        file_size_bytes=max(file_size, 1),
        content_hash=ch,
        chunk_size_bytes=chunk_size,
        total_chunks=max(total_chunks, 1),
    )


def _ingest_transfer(data: dict) -> str:
    doc = _document_for_hash(
        data['content_hash'],
        data['bytes_transferred'],
        data['total_chunks'],
        data.get('chunk_size') or 262144,
        file_name=data.get('file_name') or '',
        document_title=data.get('document_title') or '',
    )
    if data['status'] == 'COMPLETED':
        AcademicDocument.objects.filter(pk=doc.pk).update(total_downloads=doc.total_downloads + 1)
    session = TransferSession.objects.create(
        document=doc,
        source_node=None,
        target_node=None,
        transfer_type='DOWNLOAD',
        status=data['status'],
        file_size_bytes=data['bytes_transferred'] if data['status'] == 'COMPLETED' else doc.file_size_bytes,
        bytes_transferred=data['bytes_transferred'],
        chunks_transferred=data['chunks_transferred'],
        total_chunks=data['total_chunks'] or doc.total_chunks,
        parallel_seeders=data['parallel_seeders'],
        duration_seconds=data['duration_seconds'],
        average_speed_kbps=data['average_speed_kbps'],
        peak_speed_kbps=data['peak_speed_kbps'],
        tor_circuit_latency_ms=data.get('tor_circuit_latency_ms') or 0.0,
        started_at=data['started_at'],
        completed_at=data.get('completed_at') or timezone.now(),
        is_simulated=False,
        chunk_failures=data.get('chunk_failures') or 0,
        retries=data.get('retries') or 0,
    )
    return str(session.id)


def _ingest_chunk(data: dict) -> str:
    transfer = None
    if data.get('transfer_id'):
        transfer = TransferSession.objects.filter(pk=data['transfer_id']).first()
    if transfer is None and data.get('content_hash'):
        transfer = (
            TransferSession.objects.filter(document__content_hash=data['content_hash'].lower())
            .order_by('-started_at')
            .first()
        )
    if transfer is None:
        # Create a stub transfer session for orphan chunk logs
        doc = _document_for_hash(data.get('content_hash') or ('0' * 64), data['chunk_size_bytes'], 1, data['chunk_size_bytes'])
        transfer = TransferSession.objects.create(
            document=doc,
            bytes_transferred=data['chunk_size_bytes'],
            file_size_bytes=data['chunk_size_bytes'],
            chunks_transferred=1,
            total_chunks=1,
            duration_seconds=max(data['transfer_time_ms'] / 1000.0, 0.001),
            average_speed_kbps=0.0,
            peak_speed_kbps=0.0,
            started_at=data['timestamp'],
            completed_at=data['timestamp'],
            status='COMPLETED',
            is_simulated=False,
        )
    log = ChunkPerformanceLog.objects.create(
        transfer=transfer,
        chunk_index=data['chunk_index'],
        chunk_size_bytes=data['chunk_size_bytes'],
        latency_ms=data['latency_ms'],
        transfer_time_ms=data['transfer_time_ms'],
        verification_passed=data['verification_passed'],
        retry_count=data['retry_count'],
        timestamp=data['timestamp'],
    )
    return str(log.id)


def _ingest_lookup(data: dict) -> str:
    ev = LookupEvent.objects.create(
        content_hash=(data.get('content_hash') or '')[:64],
        hops=data['hops'],
        duration_ms=data['duration_ms'],
        success=data['success'],
        peer_count=data['peer_count'],
        started_at=data['started_at'],
        is_simulated=False,
    )
    return str(ev.id)


def _ingest_gossip(data: dict) -> str:
    ev = GossipPropagationEvent.objects.create(
        msg_id=data['msg_id'],
        content_hash=data['content_hash'],
        hop=data['hop'],
        propagation_ms=data['propagation_ms'],
        recorded_at=data['recorded_at'],
        is_simulated=False,
    )
    return str(ev.id)


def _ingest_presence(item: dict) -> str:
    et = item.get('churn_event_type') or item.get('presence_type') or item.get('type') or 'node_join'
    node_id = item.get('node_id') or ''
    occurred = item.get('occurred_at') or item.get('at')
    if isinstance(occurred, str):
        occurred = parse_datetime(occurred) or timezone.now()
    if occurred is None:
        occurred = timezone.now()
    # Unix epoch seconds from tracker
    if isinstance(item.get('at'), str) and item['at'].isdigit():
        from datetime import datetime, timezone as dt_tz
        occurred = datetime.fromtimestamp(int(item['at']), tz=dt_tz.utc)
    ev = ChurnEvent.objects.create(
        event_type=et if et in ('node_join', 'node_leave', 'stale_evict') else 'node_join',
        node_id=str(node_id)[:80],
        occurred_at=occurred,
        is_simulated=False,
    )
    return str(ev.id)


class TelemetryIngestAPIView(APIView):
    """
    POST /api/v1/telemetry/ingest/
    Typed batch: transfer | chunk | lookup | gossip | presence
    Legacy: bare transfer fields (no event_type) still accepted.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        items = payload if isinstance(payload, list) else [payload]
        if not items:
            return Response({'detail': 'empty payload'}, status=status.HTTP_400_BAD_REQUEST)

        created_ids = []
        errors = []
        # Link chunk events in the same batch to the transfer just created for that hash.
        batch_transfer_by_hash: dict[str, str] = {}
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append({'index': idx, 'errors': 'not an object'})
                continue
            et = item.get('event_type') or 'transfer'
            try:
                if et == 'transfer':
                    ser = TransferIngestSerializer(data=item)
                    if not ser.is_valid():
                        errors.append({'index': idx, 'errors': ser.errors})
                        continue
                    tid = _ingest_transfer(ser.validated_data)
                    created_ids.append(tid)
                    ch = (ser.validated_data.get('content_hash') or '').lower()
                    if ch:
                        batch_transfer_by_hash[ch] = tid
                elif et == 'chunk':
                    payload = dict(item)
                    ch = (payload.get('content_hash') or '').lower()
                    if not payload.get('transfer_id') and ch in batch_transfer_by_hash:
                        payload['transfer_id'] = batch_transfer_by_hash[ch]
                    ser = ChunkIngestSerializer(data=payload)
                    if not ser.is_valid():
                        errors.append({'index': idx, 'errors': ser.errors})
                        continue
                    created_ids.append(_ingest_chunk(ser.validated_data))
                elif et == 'lookup':
                    ser = LookupIngestSerializer(data=item)
                    if not ser.is_valid():
                        errors.append({'index': idx, 'errors': ser.errors})
                        continue
                    created_ids.append(_ingest_lookup(ser.validated_data))
                elif et == 'gossip':
                    ser = GossipIngestSerializer(data=item)
                    if not ser.is_valid():
                        errors.append({'index': idx, 'errors': ser.errors})
                        continue
                    created_ids.append(_ingest_gossip(ser.validated_data))
                elif et == 'presence':
                    created_ids.append(_ingest_presence(item))
                else:
                    errors.append({'index': idx, 'errors': f'unknown event_type {et}'})
            except Exception as exc:  # noqa: BLE001
                errors.append({'index': idx, 'errors': str(exc)})

        if errors and not created_ids:
            return Response({'detail': 'validation failed', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'created': len(created_ids),
                'ids': created_ids,
                'errors': errors,
                'is_simulated': False,
            },
            status=status.HTTP_201_CREATED,
        )
