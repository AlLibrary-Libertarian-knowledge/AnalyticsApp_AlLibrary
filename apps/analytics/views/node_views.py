from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from apps.analytics.models import PeerNode
from apps.analytics.serializers import PeerNodeSerializer
from apps.core.pagination import StandardResultsSetPagination

class PeerNodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para listagem e inspeção dos nós P2P da rede Tor/AlLibrary.
    Focado nos nós participantes do teste em SP e RS (Brasil).
    """
    queryset = PeerNode.objects.all().order_by('-last_seen')
    serializer_class = PeerNodeSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_online', 'region_state', 'city', 'client_version']
