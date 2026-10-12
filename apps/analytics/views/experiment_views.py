from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg, Count, Q

from apps.analytics.models import (
    TransferSession,
    ChunkPerformanceLog,
    LookupEvent,
    GossipPropagationEvent,
    ChurnEvent,
    PeerNode,
)


def _percentile(sorted_vals, p):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return round(sorted_vals[0], 3)
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return round(sorted_vals[f], 3)
    return round(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f), 3)


class ExperimentSummaryAPIView(APIView):
    """
    GET /api/v1/experiment/summary/?include_simulated=0
    Cap. 6 KPIs: p50/p95, integrity, lookup, gossip, churn.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        include_sim = request.query_params.get('include_simulated', '0') in ('1', 'true', 'True')
        t_qs = TransferSession.objects.all()
        l_qs = LookupEvent.objects.all()
        g_qs = GossipPropagationEvent.objects.all()
        c_qs = ChurnEvent.objects.all()
        if not include_sim:
            t_qs = t_qs.filter(is_simulated=False)
            l_qs = l_qs.filter(is_simulated=False)
            g_qs = g_qs.filter(is_simulated=False)
            c_qs = c_qs.filter(is_simulated=False)

        total = t_qs.count()
        completed = t_qs.filter(status='COMPLETED').count()
        timed_out = t_qs.filter(status='TIMED_OUT').count()
        failed = t_qs.filter(status='FAILED').count()

        durations = list(
            t_qs.filter(status='COMPLETED').values_list('duration_seconds', flat=True)
        )
        speeds = list(
            t_qs.filter(status='COMPLETED').values_list('average_speed_kbps', flat=True)
        )
        durations.sort()
        speeds.sort()

        chunk_total = ChunkPerformanceLog.objects.filter(transfer__in=t_qs).count()
        chunk_ok = ChunkPerformanceLog.objects.filter(
            transfer__in=t_qs, verification_passed=True
        ).count()
        # Fallback integrity from session chunk_failures when no chunk logs
        if chunk_total == 0:
            agg = t_qs.aggregate(
                fails=Count('id', filter=Q(chunk_failures__gt=0)),
            )
            integrity = round(100.0 * (1 - (agg['fails'] or 0) / total), 2) if total else None
        else:
            integrity = round(100.0 * chunk_ok / chunk_total, 2)

        lookup_durs = list(l_qs.values_list('duration_ms', flat=True))
        lookup_durs.sort()
        gossip_props = list(g_qs.values_list('propagation_ms', flat=True))
        gossip_props.sort()

        retries_avg = t_qs.aggregate(a=Avg('retries'))['a'] or 0

        return Response({
            'include_simulated': include_sim,
            'transfers': {
                'total': total,
                'completed': completed,
                'timed_out': timed_out,
                'failed': failed,
                'success_rate_percent': round((completed / total * 100) if total else 0, 1),
                'duration_seconds_p50': _percentile(durations, 50),
                'duration_seconds_p95': _percentile(durations, 95),
                'speed_kbps_p50': _percentile(speeds, 50),
                'speed_kbps_p95': _percentile(speeds, 95),
                'retries_avg': round(retries_avg, 2),
                'chunk_integrity_rate_percent': integrity,
            },
            'lookup': {
                'count': l_qs.count(),
                'success_rate_percent': round(
                    100.0 * l_qs.filter(success=True).count() / l_qs.count(), 1
                ) if l_qs.count() else 0,
                'duration_ms_p50': _percentile(lookup_durs, 50),
                'duration_ms_p95': _percentile(lookup_durs, 95),
                'avg_hops': round(l_qs.aggregate(a=Avg('hops'))['a'] or 0, 2),
            },
            'gossip': {
                'count': g_qs.count(),
                'propagation_ms_p50': _percentile(gossip_props, 50),
                'propagation_ms_p95': _percentile(gossip_props, 95),
            },
            'churn': {
                'joins': c_qs.filter(event_type='node_join').count(),
                'leaves': c_qs.filter(event_type='node_leave').count(),
                'stale_evicts': c_qs.filter(event_type='stale_evict').count(),
                'total_events': c_qs.count(),
            },
            'nodes': {
                'total': PeerNode.objects.count(),
                'online': PeerNode.objects.filter(is_online=True).count(),
            },
        })
