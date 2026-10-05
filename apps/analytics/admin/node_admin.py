from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin_mixins import AlLibraryAdminMixin
from apps.analytics.models import PeerNode

@admin.register(PeerNode)
class PeerNodeAdmin(AlLibraryAdminMixin, admin.ModelAdmin):
    list_display = (
        'node_alias_display',
        'location_badge',
        'onion_display', 
        'client_version', 
        'online_badge', 
        'reputation_score', 
        'total_chunks_served', 
        'last_seen'
    )
    list_filter = ('is_online', 'region_state', 'city', 'client_version')
    search_fields = ('node_id', 'node_alias', 'onion_address', 'city')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_seen')
    ordering = ('-last_seen',)

    @admin.display(description="Identificação do Nó")
    def node_alias_display(self, obj):
        return obj.node_alias or f"Node {str(obj.node_id)[:8]}..."

    @admin.display(description="Localização")
    def location_badge(self, obj):
        color = "#10b981" if obj.region_state == "RS" else "#3b82f6"
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">{} - {}</span>',
            color, obj.city, obj.region_state
        )

    @admin.display(description="Endereço Tor (.onion)")
    def onion_display(self, obj):
        return format_html(
            '<code style="background: #1e1e24; color: #a5d6a7; padding: 2px 6px; border-radius: 4px;">{}</code>',
            f"{obj.onion_address[:16]}...onion"
        )

    @admin.display(description="Status")
    def online_badge(self, obj):
        if obj.is_online:
            return format_html('<span style="color: #4caf50; font-weight: bold;">● Online</span>')
        return format_html('<span style="color: #f44336; font-weight: bold;">○ Offline</span>')
