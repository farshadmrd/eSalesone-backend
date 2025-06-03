import uuid
from django.db import models
from core.validators import validate_logo_file_extension

class Service(models.Model):
    """
    Represents offered services.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='media/logos/', validators=[validate_logo_file_extension])
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Type(models.Model):
    """
    Represents a type of service.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.JSONField(default=list, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    recommended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.service.title}-{self.name}"
