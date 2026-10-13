from rest_framework import serializers


class TransferIngestSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=['transfer'], required=False, default='transfer')
    content_hash = serializers.RegexField(regex=r'^[a-fA-F0-9]{32,64}$', max_length=64)
    file_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    document_title = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    status = serializers.ChoiceField(
        choices=['COMPLETED', 'FAILED', 'INTERRUPTED', 'TIMED_OUT'],
        default='COMPLETED',
    )
    bytes_transferred = serializers.IntegerField(min_value=0)
    chunks_transferred = serializers.IntegerField(min_value=0, default=0)
    total_chunks = serializers.IntegerField(min_value=0, default=0)
    parallel_seeders = serializers.IntegerField(min_value=1, default=1)
    duration_seconds = serializers.FloatField(min_value=0.001)
    average_speed_kbps = serializers.FloatField(min_value=0)
    peak_speed_kbps = serializers.FloatField(min_value=0, required=False, allow_null=True)
    chunk_failures = serializers.IntegerField(min_value=0, default=0, required=False)
    retries = serializers.IntegerField(min_value=0, default=0, required=False)
    chunk_size = serializers.IntegerField(min_value=1024, default=262144, required=False)
    tor_circuit_latency_ms = serializers.FloatField(min_value=0, required=False, allow_null=True)
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs.get('peak_speed_kbps') is None:
            attrs['peak_speed_kbps'] = round(attrs['average_speed_kbps'] * 1.15, 1)
        if attrs.get('total_chunks', 0) == 0 and attrs.get('chunks_transferred', 0) > 0:
            attrs['total_chunks'] = attrs['chunks_transferred']
        attrs['event_type'] = 'transfer'
        return attrs


# Backward-compatible alias
TelemetryIngestSerializer = TransferIngestSerializer


class ChunkIngestSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=['chunk'])
    transfer_id = serializers.UUIDField(required=False, allow_null=True)
    content_hash = serializers.RegexField(regex=r'^[a-fA-F0-9]{32,64}$', max_length=64, required=False)
    chunk_index = serializers.IntegerField(min_value=0)
    chunk_size_bytes = serializers.IntegerField(min_value=1, default=262144)
    latency_ms = serializers.FloatField(min_value=0)
    transfer_time_ms = serializers.FloatField(min_value=0)
    verification_passed = serializers.BooleanField(default=True)
    retry_count = serializers.IntegerField(min_value=0, default=0)
    timestamp = serializers.DateTimeField()


class LookupIngestSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=['lookup'])
    content_hash = serializers.CharField(max_length=64, required=False, allow_blank=True, default='')
    hops = serializers.IntegerField(min_value=0, default=0)
    duration_ms = serializers.IntegerField(min_value=0)
    success = serializers.BooleanField(default=False)
    peer_count = serializers.IntegerField(min_value=0, default=0)
    started_at = serializers.DateTimeField()


class GossipIngestSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=['gossip'])
    msg_id = serializers.CharField(max_length=64)
    content_hash = serializers.CharField(max_length=64)
    hop = serializers.IntegerField(min_value=0, default=0)
    propagation_ms = serializers.IntegerField(min_value=0)
    recorded_at = serializers.DateTimeField()


class PresenceIngestSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=['presence'])
    churn_event_type = serializers.ChoiceField(
        choices=['node_join', 'node_leave', 'stale_evict'],
        source='event_type_churn',
    )
    node_id = serializers.CharField(max_length=80)
    occurred_at = serializers.DateTimeField()

    def to_internal_value(self, data):
        # Accept both churn_event_type and nested event naming from tracker collector
        if isinstance(data, dict) and 'churn_event_type' not in data and data.get('event_type') == 'presence':
            data = {**data, 'churn_event_type': data.get('presence_type') or data.get('type') or 'node_join'}
        return super().to_internal_value(data)
