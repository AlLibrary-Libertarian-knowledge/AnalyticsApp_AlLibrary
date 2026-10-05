from django.db import models
from apps.core.models.base_model import BaseModel
from apps.analytics.models.transfer import TransferSession
from apps.analytics.models.node import PeerNode

class ChunkPerformanceLog(BaseModel):
    """
    Telemetria em nível de bloco (chunk) individual do protocolo Onion-Share.
    Mede integridade da cifra XChaCha20-Poly1305, tempo de resposta e retransmissões.
    """
    transfer = models.ForeignKey(TransferSession, on_delete=models.CASCADE, related_name='chunk_logs')
    chunk_index = models.IntegerField(verbose_name="Índice do Chunk")
    chunk_size_bytes = models.IntegerField(default=524288)
    latency_ms = models.FloatField(verbose_name="Latência do Chunk (ms)")
    transfer_time_ms = models.FloatField(verbose_name="Tempo de Baixa (ms)")
    verification_passed = models.BooleanField(default=True, verbose_name="Validação Poly1305 Aprovada")
    retry_count = models.IntegerField(default=0, verbose_name="Retransmissões")
    seeder_node = models.ForeignKey(PeerNode, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        verbose_name = "Log de Desempenho de Chunk"
        verbose_name_plural = "Logs de Desempenho de Chunks"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Chunk #{self.chunk_index} ({'OK' if self.verification_passed else 'FALHA'}) - {self.transfer_time_ms:.1f}ms"
