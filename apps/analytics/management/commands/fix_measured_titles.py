"""Rename 'Measured transfer …' documents using file names / known Cap.6 hashes."""

from django.core.management.base import BaseCommand

from apps.analytics.models import AcademicDocument
from apps.analytics.views.telemetry_ingest_views import KNOWN_DOCUMENT_TITLES


# Lab seed filenames keyed by content hash prefix (filled at runtime via --map-json optional).
LAB_NAME_HINTS = {
    "sp_handbook": "sp_handbook_p2p.pdf",
    "poa_thesis": "poa_thesis_excerpt.pdf",
    "cwb_eng": "cwb_eng_report.pdf",
    "rec_nordeste": "rec_nordeste_lib.pdf",
    "lab_shared": "lab_shared_bundle.pdf",
}


class Command(BaseCommand):
    help = "Fix AcademicDocument titles that still say Measured transfer …"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hash-title",
            action="append",
            default=[],
            help="content_hash=Title.pdf (repeatable)",
        )

    def handle(self, *args, **options):
        mapping = dict(KNOWN_DOCUMENT_TITLES)
        for item in options["hash_title"]:
            if "=" not in item:
                continue
            h, title = item.split("=", 1)
            mapping[h.strip().lower()] = title.strip()

        fixed = 0
        for doc in AcademicDocument.objects.all():
            ch = (doc.content_hash or "").lower()
            new_title = mapping.get(ch)
            if not new_title and doc.title.startswith("Measured transfer"):
                # leave unless mapped
                continue
            if new_title and doc.title != new_title:
                doc.title = new_title
                doc.save(update_fields=["title"])
                fixed += 1
                self.stdout.write(f"  {ch[:12]}… → {new_title[:60]}")

        # Also upgrade any Measured transfer whose hash matches Cap.6 known set
        for ch, title in KNOWN_DOCUMENT_TITLES.items():
            n = AcademicDocument.objects.filter(content_hash=ch).exclude(title=title).update(title=title)
            fixed += n

        self.stdout.write(self.style.SUCCESS(f"Updated {fixed} document title(s)."))
