from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin_mixins import AlLibraryAdminMixin
from apps.analytics.models import AcademicDocument

@admin.register(AcademicDocument)
class AcademicDocumentAdmin(AlLibraryAdminMixin, admin.ModelAdmin):
    list_display = (
        'title', 
        'author', 
        'category_badge', 
        'file_type_badge', 
        'formatted_size', 
        'total_chunks', 
        'total_seeds_active', 
        'total_downloads'
    )
    list_filter = ('category', 'file_type', 'publication_year')
    search_fields = ('title', 'author', 'content_hash')
    readonly_fields = ('id', 'created_at', 'updated_at', 'content_hash', 'total_chunks', 'file_size_bytes')
    ordering = ('-total_downloads',)

    @admin.display(description="Área")
    def category_badge(self, obj):
        colors = {
            'COMPUTACAO': '#2196f3',
            'ENGENHARIA': '#00bcd4',
            'SEGURANCA': '#9c27b0',
            'ECONOMIA': '#ff9800',
            'DIREITO': '#795548',
            'MATEMATICA': '#3f51b5',
            'FILOSOFIA': '#607d8b'
        }
        bg = colors.get(obj.category, '#455a64')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            bg, obj.get_category_display()
        )

    @admin.display(description="Formato")
    def file_type_badge(self, obj):
        return format_html(
            '<span style="background: #263238; color: #ffeb3b; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{}</span>',
            obj.file_type
        )

    @admin.display(description="Tamanho")
    def formatted_size(self, obj):
        return f"{obj.file_size_mb} MB"
