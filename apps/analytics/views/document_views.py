from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from apps.analytics.models import AcademicDocument
from apps.analytics.serializers import AcademicDocumentSerializer
from apps.core.pagination import StandardResultsSetPagination

class AcademicDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para catálogo acadêmico e metadados de compartilhamento em chunks.
    """
    queryset = AcademicDocument.objects.all().order_by('-total_downloads')
    serializer_class = AcademicDocumentSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'file_type', 'publication_year']
