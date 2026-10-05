from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin_mixins import AlLibraryAdminMixin
from apps.analytics.models import DailyNetworkMetric, ChunkPerformanceLog

@admin.register(DailyNetworkMetric)
class DailyNetworkMetricAdmin(AlLibraryAdminMixin, admin.ModelAdmin):
    list_display = (
        'date', 
        'activity_badge', 
        'active_nodes_peak', 
        'total_transfers', 
        'volume_display', 
        'avg_download_speed_display', 
        'chunk_integrity_rate', 
        'notes'
    )
    list_filter = ('is_active_day', 'date')
    date_hierarchy = 'date'
    ordering = ('-date',)

    @admin.display(description="Status do Dia")
    def activity_badge(self, obj):
        if obj.is_active_day:
            return format_html('<span style="color: #4caf50; font-weight: bold;">● Dia com Tráfego</span>')
        return format_html('<span style="color: #ff9800; font-weight: bold;">⏸ Pausa / Manutenção</span>')

    @admin.display(description="Volume Trafegado")
    def volume_display(self, obj):
        if obj.data_transferred_mb >= 1024:
            return f"{obj.data_transferred_mb / 1024:.2f} GB"
        return f"{obj.data_transferred_mb:.1f} MB"

    @admin.display(description="Velocidade Download")
    def avg_download_speed_display(self, obj):
        if obj.avg_download_speed_kbps >= 1024:
            return f"{obj.avg_download_speed_kbps / 1024:.2f} MB/s"
        return f"{obj.avg_download_speed_kbps:.1f} KB/s"

@admin.register(ChunkPerformanceLog)
class ChunkPerformanceLogAdmin(AlLibraryAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'transfer', 'chunk_index', 'latency_ms', 'transfer_time_ms', 'verification_badge', 'retry_count')
    list_filter = ('verification_passed', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    @admin.display(description="Verificação XChaCha20")
    def verification_badge(self, obj):
        if obj.verification_passed:
            return format_html('<span style="color: #4caf50;">✓ Poly1305 OK</span>')
        return format_html('<span style="color: #f44336; font-weight: bold;">✗ Hash Mismatch</span>')
