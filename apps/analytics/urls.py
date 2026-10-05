from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.analytics.views import (
    PeerNodeViewSet,
    AcademicDocumentViewSet,
    TransferSessionViewSet,
    AnalyticsOverviewAPIView,
    SpeedBenchmarkAPIView,
    DailyTimelineAPIView
)

router = DefaultRouter()
router.register(r'nodes', PeerNodeViewSet, basename='node')
router.register(r'documents', AcademicDocumentViewSet, basename='document')
router.register(r'transfers', TransferSessionViewSet, basename='transfer')

urlpatterns = [
    path('overview/', AnalyticsOverviewAPIView.as_view(), name='analytics-overview'),
    path('speed-benchmarks/', SpeedBenchmarkAPIView.as_view(), name='analytics-speed-benchmarks'),
    path('timeline/', DailyTimelineAPIView.as_view(), name='analytics-timeline'),
    path('', include(router.urls)),
]
