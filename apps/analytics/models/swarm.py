from django.db import models
from apps.core.models.base_model import BaseModel
from apps.analytics.models.document import AcademicDocument

class SwarmSnapshot(BaseModel):
    """
    Snapshots de presença e saúde do swarm para cada documento acadêmico.
    Dados obtidos periodicamente via rota /lobby e /swarm/:hash do Tracker Rust.
    """
    HEALTH_CHOICES = [
        ('EXCELLENT', 'Excelente (>= 5 seeders)'),
        ('HEALTHY', 'Saudável (2 a 4 seeders)'),
        ('DEGRADED', 'Degradado (1 seeder solitário)'),
        ('CRITICAL', 'Crítico (0 seeders online)'),
    ]

    document = models.ForeignKey(AcademicDocument, on_delete=models.CASCADE, related_name='swarm_snapshots')
    active_seeders = models.IntegerField(verbose_name="Seeders Ativos")
    active_leechers = models.IntegerField(default=0, verbose_name="Leechers Concorrentes")
    swarm_ratio = models.FloatField(default=1.0, verbose_name="Razão S/L")
    health_status = models.CharField(max_length=20, choices=HEALTH_CHOICES, default='HEALTHY', db_index=True)
    timestamp = models.DateTimeField(db_index=True, verbose_name="Instante da Amostra")

    class Meta:
        verbose_name = "Snapshot de Swarm"
        verbose_name_plural = "Snapshots de Swarm"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Swarm: {self.document.title[:30]} | {self.active_seeders} Seeds | {self.health_status}"
