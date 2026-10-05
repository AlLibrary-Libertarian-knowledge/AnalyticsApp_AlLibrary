from rest_framework import serializers
from apps.analytics.models import AcademicDocument

class AcademicDocumentSerializer(serializers.ModelSerializer):
    file_size_mb = serializers.FloatField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)

    class Meta:
        model = AcademicDocument
        fields = [
            'id',
            'title',
            'author',
            'category',
            'category_display',
            'file_type',
            'file_type_display',
            'file_size_bytes',
            'file_size_mb',
            'content_hash',
            'chunk_size_bytes',
            'total_chunks',
            'cipher',
            'swarm_link',
            'publication_year',
            'total_downloads',
            'total_seeds_active',
        ]
