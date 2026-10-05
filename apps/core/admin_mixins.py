from django.contrib import admin, messages
from django.http import HttpResponse
from django.db import connection
import csv

class AlLibraryAdminMixin:
    """
    Mixin para o Django Admin / Jazzmin no ecossistema AlLibrary:
    1. Ação de exportação universal para CSV (útil para extração de tabelas para o TCC).
    2. Monitoramento de volumetria em disco da tabela.
    """
    actions = ['export_as_csv']

    @admin.action(description="📥 Exportar Selecionados para Relatório TCC (CSV)")
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={meta.db_table}_tcc_export.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                row.append(str(val))
            writer.writerow(row)

        return response

    def changelist_view(self, request, extra_context=None):
        try:
            table_name = self.model._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT pg_total_relation_size('{table_name}');")
                size_bytes = cursor.fetchone()[0]
                size_mb = size_bytes / (1024 * 1024)
                self.message_user(
                    request, 
                    f"📊 Volumetria desta tabela ({table_name}): {size_mb:.2f} MB", 
                    level=messages.INFO
                )
        except Exception:
            pass
        return super().changelist_view(request, extra_context)
