from django.db import models
from apps.core.models.base_model import BaseModel
from apps.analytics.models.transfer import TransferSession


class LookupEvent(BaseModel):
    """Measured Kademlia FIND_VALUE / FIND_NODE from desktop experiment plane."""
    content_hash = models.CharField(max_length=64, blank=True, db_index=True)
    hops = models.IntegerField(default=0)
    duration_ms = models.IntegerField()
    success = models.BooleanField(default=False, db_index=True)
    peer_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(db_index=True)
    is_simulated = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Evento de Lookup DHT"
        ordering = ['-started_at']


class GossipPropagationEvent(BaseModel):
    """Epidemic gossip sighting (propagation delay from origin)."""
    msg_id = models.CharField(max_length=64, db_index=True)
    content_hash = models.CharField(max_length=64, db_index=True)
    hop = models.IntegerField(default=0)
    propagation_ms = models.IntegerField()
    recorded_at = models.DateTimeField(db_index=True)
    is_simulated = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Evento de Gossip"
        ordering = ['-recorded_at']


class ChurnEvent(BaseModel):
    """Anonymous presence churn from tracker (join/leave/stale_evict)."""
    EVENT_CHOICES = [
        ('node_join', 'Join'),
        ('node_leave', 'Leave'),
        ('stale_evict', 'Stale Evict'),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, db_index=True)
    node_id = models.CharField(max_length=80, db_index=True)
    occurred_at = models.DateTimeField(db_index=True)
    is_simulated = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Evento de Churn"
        ordering = ['-occurred_at']
