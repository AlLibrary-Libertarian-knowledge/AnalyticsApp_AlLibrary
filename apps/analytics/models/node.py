from django.db import models
from apps.core.models.base_model import BaseModel

class PeerNode(BaseModel):
    """
    Representação dos nós da rede P2P da AlLibrary (Onion Nodes).
    Nós de participantes dos experimentos do TCC (Sorocaba/SP e parceiros).
    """
    node_id = models.UUIDField(unique=True, db_index=True, verbose_name="Node ID")
    node_alias = models.CharField(max_length=100, blank=True, verbose_name="Identificação / Local")
    onion_address = models.CharField(max_length=120, unique=True, db_index=True, verbose_name="Endereço Hidden Service (.onion)")
    client_version = models.CharField(max_length=20, default="0.0.2", verbose_name="Versão do Cliente")
    
    country_code = models.CharField(max_length=5, default="BR", verbose_name="País")
    region_state = models.CharField(max_length=10, default="SP", verbose_name="UF")
    city = models.CharField(max_length=100, default="Sorocaba", verbose_name="Cidade")
    
    is_online = models.BooleanField(default=True, db_index=True, verbose_name="Status Online")
    last_seen = models.DateTimeField(db_index=True, verbose_name="Última Atividade")
    
    total_chunks_served = models.BigIntegerField(default=0, verbose_name="Chunks Servidos (Seed)")
    total_bytes_uploaded = models.BigIntegerField(default=0, verbose_name="Bytes Enviados")
    total_bytes_downloaded = models.BigIntegerField(default=0, verbose_name="Bytes Baixados")
    
    reputation_score = models.FloatField(default=100.0, verbose_name="Reputação (%)")

    class Meta:
        verbose_name = "Nó P2P (Peer)"
        verbose_name_plural = "Nós P2P (Peers)"
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.node_alias or str(self.node_id)[:8]} ({self.city} - {self.region_state})"
