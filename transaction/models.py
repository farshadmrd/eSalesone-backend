from django.db import models
import uuid
from decimal import Decimal
import json

class Transaction(models.Model):
    """
    Represents a financial transaction in the system.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    basket = models.JSONField(default=list, help_text="Array of items, each with service_type_id and quantity")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)  # Format: MM/YYYY
    cvv = models.CharField(max_length=4, blank=True, null=True)
    amount = models.FloatField(default=0.00, help_text="Total amount for the transaction")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def calculate_amount_from_basket(self):
        """
        Calculate the total amount from basket items using service type IDs.
        """
        from service.models import Type
        total = Decimal('0.00')
        if self.basket:
            for item in self.basket:
                if all(key in item for key in ['service_type_id', 'quantity']):
                    try:
                        service_type = Type.objects.get(id=item['service_type_id'])
                        quantity = int(item['quantity'])
                        total += service_type.price * quantity
                    except Type.DoesNotExist:
                        continue  # Skip invalid service types
        return total
    
    def calculate_tax_amount(self, tax_rate=Decimal('0.10')):
        """
        Calculate tax amount based on basket total (default 10% tax).
        """
        subtotal = self.calculate_amount_from_basket()
        return subtotal * tax_rate
    
    def get_total_with_tax(self, tax_rate=Decimal('0.10')):
        """
        Get total amount including tax.
        """
        subtotal = self.calculate_amount_from_basket()
        tax = subtotal * tax_rate
        return subtotal + tax
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate amount from basket if not set.
        Also ensure UUIDs in basket are converted to strings for JSON serialization.
        """
        # Convert UUID objects to strings in basket data
        if self.basket:
            import uuid as uuid_module
            for item in self.basket:
                for key, value in item.items():
                    if isinstance(value, uuid_module.UUID):
                        item[key] = str(value)
        
        if self.amount == 0.00 and self.basket:
            self.amount = float(self.get_total_with_tax())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.id} - {self.full_name} ({self.status})"
