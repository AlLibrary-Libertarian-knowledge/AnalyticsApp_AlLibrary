from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin_mixins import AlLibraryAdminMixin
from apps.analytics.models import TransferSession

@admin.register(TransferSession)
class TransferSessionAdmin(AlLibraryAdminMixin, admin.ModelAdmin):
    list_display = (
        'started_at', 
        'document_title', 
        'transfer_type', 
        'status_badge', 
        'parallel_seeders', 
        'average_speed_display', 
        'peak_speed_display', 
        'tor_circuit_latency_ms', 
        'duration_seconds'
    )
    list_filter = ('status', 'transfer_type', 'parallel_seeders')
    search_fields = ('document__title', 'document__content_hash')
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'started_at', 'completed_at')

    @admin.display(description="Documento")
    def document_title(self, obj):
        return obj.document.title[:35] + ("..." if len(obj.document.title) > 35 else "")

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            'COMPLETED': '#4caf50',
            'FAILED': '#f44336',
            'INTERRUPTED': '#ff9800',
            'TIMED_OUT': '#9e9e9e'
        }
        color = colors.get(obj.status, '#ffffff')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())

    @admin.display(description="Velocidade Média")
    def average_speed_display(self, obj):
        if obj.average_speed_kbps >= 1024:
            return f"{obj.average_speed_kbps / 1024:.2f} MB/s"
        return f"{obj.average_speed_kbps:.1f} KB/s"

    @admin.display(description="Pico")
    def peak_speed_display(self, obj):
        if obj.peak_speed_kbps >= 1024:
            return f"{obj.peak_speed_kbps / 1024:.2f} MB/s"
        return f"{obj.peak_speed_kbps:.1f} KB/s"
