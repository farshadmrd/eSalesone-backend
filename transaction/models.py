from django.db import models
import uuid
from decimal import Decimal

class Basket(models.Model):
    """
    Represents a shopping basket in the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    services = models.ManyToManyField('service.Service', related_name='baskets', blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))    
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Basket {self.id} created at {self.created_at}"

class Transaction(models.Model):
    """
    Represents a financial transaction in the system.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    basket = models.ForeignKey('Basket', on_delete=models.CASCADE, related_name='transactions', blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    expiry_date= models.CharField(max_length=7, blank=True, null=True)  # Format: MM/YYYY
    cvv = models.CharField(max_length=4, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.id} - ({self.status})"
