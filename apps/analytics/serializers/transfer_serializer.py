from rest_framework import serializers
from apps.analytics.models import TransferSession

class TransferSessionSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_author = serializers.CharField(source='document.author', read_only=True)
    document_format = serializers.CharField(source='document.file_type', read_only=True)
    average_speed_mbps = serializers.FloatField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transfer_type_display = serializers.CharField(source='get_transfer_type_display', read_only=True)

    class Meta:
        model = TransferSession
        fields = [
            'id',
            'document',
            'document_title',
            'document_author',
            'document_format',
            'source_node',
            'target_node',
            'transfer_type',
            'transfer_type_display',
            'status',
            'status_display',
            'file_size_bytes',
            'bytes_transferred',
            'chunks_transferred',
            'total_chunks',
            'parallel_seeders',
            'duration_seconds',
            'average_speed_kbps',
            'average_speed_mbps',
            'peak_speed_kbps',
            'tor_circuit_latency_ms',
            'started_at',
            'completed_at',
        ]
