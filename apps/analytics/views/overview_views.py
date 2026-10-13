from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg, Sum, Count, Max, Min
from apps.analytics.models import (
    PeerNode,
    AcademicDocument,
    TransferSession,
    ChunkPerformanceLog,
)


def _include_simulated(request) -> bool:
    return request.query_params.get('include_simulated', '0') in ('1', 'true', 'True')


class AnalyticsOverviewAPIView(APIView):
    """
    Endpoint agregador de KPIs centrais para o Dashboard Next.js.
    Por padrão usa apenas telemetria medida (is_simulated=False).
    Passe ?include_simulated=1 para misturar o seed do TCC.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        include_sim = _include_simulated(request)
        t_qs = TransferSession.objects.all()
        if not include_sim:
            t_qs = t_qs.filter(is_simulated=False)

        chunk_qs = ChunkPerformanceLog.objects.all()
        if not include_sim:
            chunk_qs = chunk_qs.filter(transfer__is_simulated=False)

        total_nodes = PeerNode.objects.count()
        online_nodes = PeerNode.objects.filter(is_online=True).count()

        total_documents = AcademicDocument.objects.count()
        total_transfers = t_qs.count()
        completed_transfers = t_qs.filter(status='COMPLETED').count()
        simulated_transfers = TransferSession.objects.filter(is_simulated=True).count()
        measured_transfers = TransferSession.objects.filter(is_simulated=False).count()

        transfers_agg = t_qs.filter(status='COMPLETED').aggregate(
            total_bytes=Sum('bytes_transferred'),
            avg_speed=Avg('average_speed_kbps'),
            peak_speed=Max('peak_speed_kbps'),
            avg_latency=Avg('tor_circuit_latency_ms'),
        )

        total_gb = round((transfers_agg['total_bytes'] or 0) / (1024 * 1024 * 1024), 2)
        avg_speed_kbps = round(transfers_agg['avg_speed'] or 0, 1)
        avg_speed_mbps = round(avg_speed_kbps / 1024, 2)

        single_seed_speed = t_qs.filter(
            status='COMPLETED',
            parallel_seeders=1,
        ).aggregate(avg=Avg('average_speed_kbps'))['avg'] or 0

        multi_seed_speed = t_qs.filter(
            status='COMPLETED',
            parallel_seeders__gt=1,
        ).aggregate(avg=Avg('average_speed_kbps'))['avg'] or 0

        if include_sim:
            format_distribution = AcademicDocument.objects.values('file_type').annotate(
                count=Count('id'),
                total_downloads=Sum('total_downloads'),
            ).order_by('-count')
            category_distribution = AcademicDocument.objects.values('category').annotate(
                count=Count('id'),
            ).order_by('-count')
        else:
            # Measured mode: formats from documents that appear in measured transfers
            # or that have any swarm snapshot (lobby-synced).
            from apps.analytics.models import SwarmSnapshot

            live_hashes = set(
                SwarmSnapshot.objects.order_by('-timestamp')
                .values_list('document_id', flat=True)[:200]
            )
            measured_doc_ids = set(
                t_qs.exclude(document_id=None).values_list('document_id', flat=True)
            )
            doc_ids = live_hashes | measured_doc_ids
            docs = AcademicDocument.objects.filter(id__in=doc_ids) if doc_ids else AcademicDocument.objects.none()
            format_distribution = docs.values('file_type').annotate(
                count=Count('id'),
                total_downloads=Sum('total_downloads'),
            ).order_by('-count')
            category_distribution = docs.values('category').annotate(
                count=Count('id'),
            ).order_by('-count')

        chunk_count = chunk_qs.count()
        if chunk_count:
            integrity = round(
                100.0 * chunk_qs.filter(verification_passed=True).count() / chunk_count,
                2,
            )
        elif total_transfers:
            integrity = round(
                100.0
                * (1 - t_qs.filter(chunk_failures__gt=0).count() / total_transfers),
                2,
            )
        else:
            integrity = None

        return Response({
            "include_simulated": include_sim,
            "kpis": {
                "total_nodes": total_nodes,
                "online_nodes": online_nodes,
                "total_academic_documents": total_documents,
                "total_transfers": total_transfers,
                "simulated_transfers": simulated_transfers,
                "measured_transfers": measured_transfers,
                "success_rate_percent": round(
                    (completed_transfers / total_transfers * 100) if total_transfers > 0 else 100,
                    1,
                ),
                "total_data_transferred_gb": total_gb,
                "avg_download_speed_kbps": avg_speed_kbps,
                "avg_download_speed_mbps": avg_speed_mbps,
                "peak_speed_mbps": round((transfers_agg['peak_speed'] or 0) / 1024, 2),
                "avg_tor_latency_ms": round(transfers_agg['avg_latency'] or 0, 1),
                "chunk_integrity_rate_percent": integrity,
            },
            "scientific_benchmarks": {
                "single_seed_avg_kbps": round(single_seed_speed, 1),
                "single_seed_avg_mbps": round(single_seed_speed / 1024, 2),
                "multi_seed_avg_kbps": round(multi_seed_speed, 1),
                "multi_seed_avg_mbps": round(multi_seed_speed / 1024, 2),
                "speed_gain_multiplier": round(multi_seed_speed / single_seed_speed, 2)
                if single_seed_speed > 0
                else 0,
            },
            "format_distribution": format_distribution,
            "category_distribution": category_distribution,
        })


class SpeedBenchmarkAPIView(APIView):
    """
    Curva de velocidade por seeders. Default: measured-only (?include_simulated=1 para seed).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        include_sim = _include_simulated(request)
        qs = TransferSession.objects.filter(status='COMPLETED')
        if not include_sim:
            qs = qs.filter(is_simulated=False)

        benchmarks = qs.values('parallel_seeders').annotate(
            avg_speed_kbps=Avg('average_speed_kbps'),
            peak_speed_kbps=Max('peak_speed_kbps'),
            min_speed_kbps=Min('average_speed_kbps'),
            transfers_count=Count('id'),
        ).order_by('parallel_seeders')

        data = []
        for b in benchmarks:
            data.append({
                "parallel_seeders": b['parallel_seeders'],
                "avg_speed_kbps": round(b['avg_speed_kbps'] or 0, 1),
                "avg_speed_mbps": round((b['avg_speed_kbps'] or 0) / 1024, 2),
                "peak_speed_mbps": round((b['peak_speed_kbps'] or 0) / 1024, 2),
                "sample_transfers_count": b['transfers_count'],
            })

        return Response(data)


class DailyTimelineAPIView(APIView):
    """
    Histórico diário da rede de Julho a Outubro de 2026.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.analytics.models import DailyNetworkMetric
        from apps.analytics.serializers import DailyNetworkMetricSerializer

        metrics = DailyNetworkMetric.objects.all().order_by('date')
        serializer = DailyNetworkMetricSerializer(metrics, many=True)
        return Response(serializer.data)
