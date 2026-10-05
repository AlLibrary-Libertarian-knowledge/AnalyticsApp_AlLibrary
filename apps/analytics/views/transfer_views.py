from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from apps.analytics.models import TransferSession
from apps.analytics.serializers import TransferSessionSerializer
from apps.core.pagination import StandardResultsSetPagination

class TransferSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para sessões de transferência P2P.
    Utiliza select_related para evitar N+1 queries conforme padrão SmartLab.
    """
    queryset = TransferSession.objects.select_related('document', 'source_node', 'target_node').order_by('-started_at')
    serializer_class = TransferSessionSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'transfer_type', 'parallel_seeders']
