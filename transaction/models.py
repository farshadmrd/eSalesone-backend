from django.db import models
import uuid
from decimal import Decimal

class BasketItem(models.Model):
    """
    Intermediate model to store quantity of each service type in a basket.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    basket = models.ForeignKey('Basket', on_delete=models.CASCADE, related_name='items')
    service_type = models.ForeignKey('service.Type', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('basket', 'service_type')  # Prevent duplicate items
        ordering = ['created_at']
    
    def get_total_price(self):
        """Calculate total price for this item (price * quantity)."""
        return self.service_type.price * self.quantity
    
    def __str__(self):
        return f"{self.service_type} x{self.quantity} in {self.basket.id}"

class Basket(models.Model):
    """
    Represents a shopping basket in the system.
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))    
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='PENDING', choices=STATUS_CHOICES)
    
    class Meta:
        ordering = ['-created_at']
    
    def calculate_total_amount(self):
        """
        Calculate total amount based on the prices and quantities of selected service types.
        """
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.get_total_price()
        return total
    
    def update_totals(self):
        """
        Update total_amount and tax_amount based on selected types and quantities.
        """
        self.total_amount = self.calculate_total_amount()
        # Calculate 10% tax on the total amount
        self.tax_amount = self.total_amount * Decimal('0.10')  # 10% tax
        self.save()
    
    def add_item(self, service_type, quantity=1):
        """
        Add or update an item in the basket.
        """
        item, created = BasketItem.objects.get_or_create(
            basket=self,
            service_type=service_type,
            defaults={'quantity': quantity}
        )
        if not created:
            # Item already exists, update quantity
            item.quantity += quantity
            item.save()
        self.update_totals()
        return item
    
    def remove_item(self, service_type):
        """
        Remove an item from the basket.
        """
        try:
            item = BasketItem.objects.get(basket=self, service_type=service_type)
            item.delete()
            self.update_totals()
            return True
        except BasketItem.DoesNotExist:
            return False
    
    def update_item_quantity(self, service_type, quantity):
        """
        Update the quantity of an existing item.
        """
        try:
            item = BasketItem.objects.get(basket=self, service_type=service_type)
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()
            self.update_totals()
            return True
        except BasketItem.DoesNotExist:
            return False
    
    def __str__(self):
        items_list = ", ".join([f"{item.service_type} x{item.quantity}" for item in self.items.all()])
        return f"Basket [{items_list}] created at {self.created_at}"
    
    def create_transaction(self, transaction_data):
        """
        Create a transaction from this basket with the basket's total amount.
        """
        from .models import Transaction
        
        # Calculate total including tax
        total_with_tax = self.total_amount + self.tax_amount
        
        # Create transaction with basket data
        transaction = Transaction.objects.create(
            basket=self,
            amount=total_with_tax,
            **transaction_data
        )
        
        # Mark basket as completed
        self.status = 'COMPLETED'
        self.save()
        
        return transaction

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
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def set_amount_from_basket(self):
        """
        Set the transaction amount equal to the basket's total amount including tax.
        """
        if self.basket:
            # Calculate total including tax
            self.amount = self.basket.total_amount + self.basket.tax_amount
            return self.amount
        return None
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set amount from basket if basket exists and amount is not set.
        """
        # If basket exists and amount is 0, None, or not set, calculate from basket
        if self.basket and (self.amount is None or self.amount == Decimal('0.00')):
            self.set_amount_from_basket()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.id} - ({self.status})"
