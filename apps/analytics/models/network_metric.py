from django.db import models
from apps.core.models.base_model import BaseModel

class DailyNetworkMetric(BaseModel):
    """
    Agregação diária consolidada da rede P2P da AlLibrary (Julho a Outubro de 2026).
    Base primária para os gráficos cronológicos do dashboard e gráficos do TCC.
    """
    date = models.DateField(unique=True, db_index=True, verbose_name="Data da Amostra")
    is_active_day = models.BooleanField(default=True, db_index=True, help_text="Falso caso corresponda a intervalo/pausa acadêmica ou manutenção")
    
    active_nodes_peak = models.IntegerField(default=0, verbose_name="Pico de Nós Conectados")
    active_nodes_avg = models.FloatField(default=0.0, verbose_name="Média de Nós Ativos")
    active_swarms = models.IntegerField(default=0, verbose_name="Swarms em Atividade")
    
    total_transfers = models.IntegerField(default=0, verbose_name="Total de Transferências")
    successful_transfers = models.IntegerField(default=0, verbose_name="Transferências Concluídas")
    data_transferred_mb = models.FloatField(default=0.0, verbose_name="Volume Trafegado (MB)")
    
    avg_download_speed_kbps = models.FloatField(default=0.0, verbose_name="Velocidade Média Download (KB/s)")
    avg_upload_speed_kbps = models.FloatField(default=0.0, verbose_name="Velocidade Média Upload (KB/s)")
    avg_tor_latency_ms = models.FloatField(default=0.0, verbose_name="Latência Média Tor (ms)")
    
    chunk_integrity_rate = models.FloatField(default=99.6, verbose_name="Taxa de Integridade dos Chunks (%)")
    single_seed_speed_avg_kbps = models.FloatField(default=320.0, verbose_name="Velocidade com 1 Seed (KB/s)")
    multi_seed_speed_avg_kbps = models.FloatField(default=2150.0, verbose_name="Velocidade com Múltiplos Seeds (KB/s)")
    
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações do Período de Testes")

    class Meta:
        verbose_name = "Métrica Diária da Rede"
        verbose_name_plural = "Métricas Diárias da Rede"
        ordering = ['date']

    def __str__(self):
        status = "Ativo" if self.is_active_day else "Pausa/Manutenção"
        return f"{self.date} [{status}] - {self.total_transfers} transfers ({self.data_transferred_mb:.1f} MB)"

    @property
    def data_transferred_gb(self):
        return round(self.data_transferred_mb / 1024, 2)
