from rest_framework import serializers
from apps.analytics.models import PeerNode

class PeerNodeSerializer(serializers.ModelSerializer):
    location_display = serializers.SerializerMethodField()

    class Meta:
        model = PeerNode
        fields = [
            'id',
            'node_id',
            'node_alias',
            'onion_address',
            'client_version',
            'country_code',
            'region_state',
            'city',
            'location_display',
            'is_online',
            'last_seen',
            'total_chunks_served',
            'total_bytes_uploaded',
            'total_bytes_downloaded',
            'reputation_score',
        ]

    def get_location_display(self, obj):
        return f"{obj.city}/{obj.region_state}"
