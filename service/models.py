from django.db import models

class Service(models.Model):
    """
    Represents offered services.
    """
    title = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='media/logos/')
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Type(models.Model):
    """
    Represents a type of service.
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
