from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin_mixins import AlLibraryAdminMixin
from apps.analytics.models import SwarmSnapshot

@admin.register(SwarmSnapshot)
class SwarmSnapshotAdmin(AlLibraryAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'document_title', 'active_seeders', 'active_leechers', 'swarm_ratio', 'health_badge')
    list_filter = ('health_status', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    @admin.display(description="Documento")
    def document_title(self, obj):
        return obj.document.title[:40]

    @admin.display(description="Saúde do Swarm")
    def health_badge(self, obj):
        colors = {
            'EXCELLENT': '#2e7d32',
            'HEALTHY': '#388e3c',
            'DEGRADED': '#f57c00',
            'CRITICAL': '#d32f2f',
        }
        color = colors.get(obj.health_status, '#333333')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_health_status_display())
