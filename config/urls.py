from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AlLibrary P2P Telemetry & Analytics API",
        default_version='v1',
        description=(
            "API de telemetria e análise quantitativa da rede P2P AlLibrary.\n"
            "Métricas de throughput, latência de circuitos Tor, integridade de chunks "
            "e paralelismo de swarms para o TCC (Protocolo P2P Onion)."
        ),
        terms_of_service="https://github.com/AlLibrary-Libertarian-knowledge",
        contact=openapi.Contact(email="contato@allibrary.org"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Painel Administrativo com Tema Jazzmin
    path('admin/', admin.site.urls),

    # Endpoints de Telemetria e Analytics
    path('api/v1/', include('apps.analytics.urls')),

    # Documentação Swagger e ReDoc
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
