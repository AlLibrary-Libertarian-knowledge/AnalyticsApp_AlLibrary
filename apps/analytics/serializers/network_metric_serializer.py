from rest_framework import serializers
from apps.analytics.models import DailyNetworkMetric

class DailyNetworkMetricSerializer(serializers.ModelSerializer):
    data_transferred_gb = serializers.FloatField(read_only=True)

    class Meta:
        model = DailyNetworkMetric
        fields = [
            'id',
            'date',
            'is_active_day',
            'active_nodes_peak',
            'active_nodes_avg',
            'active_swarms',
            'total_transfers',
            'successful_transfers',
            'data_transferred_mb',
            'data_transferred_gb',
            'avg_download_speed_kbps',
            'avg_upload_speed_kbps',
            'avg_tor_latency_ms',
            'chunk_integrity_rate',
            'single_seed_speed_avg_kbps',
            'multi_seed_speed_avg_kbps',
            'notes',
        ]
