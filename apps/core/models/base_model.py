import uuid
from django.db import models

class BaseModel(models.Model):
    """
    Base model that provides a UUID primary key and timestamp fields.
    Adheres to the architectural standard established in SmartLab Core.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
