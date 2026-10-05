from django.db import models
from apps.core.models.base_model import BaseModel
from apps.analytics.models.document import AcademicDocument
from apps.analytics.models.node import PeerNode

class TransferSession(BaseModel):
    """
    Sessão completa de download ou upload de arquivo acadêmico via Tor/Swarm.
    Fundamental para o capítulo de Resultados do TCC (taxa de transferência,
    paralelismo de seeds e latência Tor).
    """
    TRANSFER_TYPE_CHOICES = [
        ('DOWNLOAD', 'Download de Documento'),
        ('UPLOAD', 'Upload / Anúncio Inicial'),
        ('SWARM_RESEED', 'Replicação Automática Swarm'),
    ]

    STATUS_CHOICES = [
        ('COMPLETED', 'Concluído com Sucesso'),
        ('FAILED', 'Falha Criptográfica / Hash Incorreto'),
        ('INTERRUPTED', 'Interrompido pelo Usuário'),
        ('TIMED_OUT', 'Timeout de Circuito Tor'),
    ]

    document = models.ForeignKey(AcademicDocument, on_delete=models.CASCADE, related_name='transfers')
    source_node = models.ForeignKey(PeerNode, null=True, blank=True, on_delete=models.SET_NULL, related_name='transfers_as_source')
    target_node = models.ForeignKey(PeerNode, null=True, blank=True, on_delete=models.SET_NULL, related_name='transfers_as_target')
    
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, default='DOWNLOAD', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED', db_index=True)
    
    file_size_bytes = models.BigIntegerField()
    bytes_transferred = models.BigIntegerField()
    chunks_transferred = models.IntegerField()
    total_chunks = models.IntegerField()
    
    parallel_seeders = models.IntegerField(default=1, help_text="Quantidade de peers que participaram do envio simultâneo de chunks")
    duration_seconds = models.FloatField(verbose_name="Duração (segundos)")
    average_speed_kbps = models.FloatField(db_index=True, verbose_name="Velocidade Média (KB/s)")
    peak_speed_kbps = models.FloatField(verbose_name="Velocidade de Pico (KB/s)")
    tor_circuit_latency_ms = models.FloatField(default=350.0, verbose_name="Latência Tor (ms)")
    
    started_at = models.DateTimeField(db_index=True, verbose_name="Início da Transferência")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Conclusão")

    class Meta:
        verbose_name = "Sessão de Transferência"
        verbose_name_plural = "Sessões de Transferência"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.get_transfer_type_display()}: {self.document.title[:25]} - {self.average_speed_kbps:.1f} KB/s ({self.parallel_seeders} seeds)"

    @property
    def average_speed_mbps(self):
        return round(self.average_speed_kbps / 1024, 2)
