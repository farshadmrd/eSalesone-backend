from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from .models import Transaction, Basket, BasketItem

class BasketItemSerializer(serializers.ModelSerializer):
    """
    Serializer for BasketItem model.
    """
    service_type_name = serializers.CharField(source='service_type.__str__', read_only=True)
    total_price = serializers.DecimalField(source='get_total_price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = BasketItem
        fields = [
            'id',
            'service_type',
            'service_type_name',
            'quantity',
            'total_price',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class BasketSerializer(serializers.ModelSerializer):
    """
    Serializer for Basket model.
    """
    items = BasketItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    calculated_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Basket
        fields = [
            'id',
            'items',
            'items_count',
            'total_amount',
            'calculated_total',
            'tax_amount',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_amount', 'tax_amount']
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_calculated_total(self, obj):
        return obj.calculate_total_amount()
    
    def save(self, **kwargs):
        """
        Override save to automatically update totals when basket is saved.
        """
        instance = super().save(**kwargs)
        # Update totals after saving
        instance.update_totals()
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    basket_details = BasketSerializer(source='basket', read_only=True)
    basket_total_with_tax = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'basket',
            'basket_details',
            'basket_total_with_tax',
            'full_name',
            'email',
            'phone_number',
            'address',
            'city',
            'state',
            'zip_code',
            'card_number',
            'expiry_date',
            'cvv',
            'amount',
            'status',
            'description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'card_number': {'write_only': True},
            'expiry_date': {'write_only': True},
            'cvv': {'write_only': True},
        }
    
    def get_basket_total_with_tax(self, obj):
        """Get the total amount including tax from the associated basket."""
        if obj.basket:
            return obj.basket.total_amount + obj.basket.tax_amount
        return None
    
    def validate_expiry_date(self, value):
        """
        Validate that expiry date is in the future.
        Expected format: MM/YYYY
        """
        if value:
            try:
                # Parse the expiry date
                month, year = value.split('/')
                month = int(month)
                year = int(year)
                
                # Validate month range
                if month < 1 or month > 12:
                    raise serializers.ValidationError("Month must be between 01 and 12")
                
                # Create a date object for the last day of the expiry month
                from calendar import monthrange
                last_day = monthrange(year, month)[1]
                expiry_date = datetime(year, month, last_day)
                
                # Check if the expiry date is in the future
                current_date = timezone.now()
                if timezone.make_aware(expiry_date) <= current_date:
                    raise serializers.ValidationError("Expiry date must be in the future")
                
            except ValueError:
                raise serializers.ValidationError("Expiry date must be in MM/YYYY format")
        
        return value
    
    def validate_cvv(self, value):
        """
        Validate that CVV is exactly 3 digits.
        """
        if value:
            if not value.isdigit() or len(value) != 3:
                raise serializers.ValidationError("CVV must be exactly 3 digits")
        
        return value
    
    def validate_card_number(self, value):
        """
        Validate card number and handle special test cases.
        """
        if value:
            # Remove any spaces or dashes
            clean_card = value.replace(' ', '').replace('-', '')
            
            # Check for special test card numbers
            if clean_card in ['1', '2', '3']:
                return clean_card  # These are valid test cases
            
            # For other card numbers, validate length (typically 13-19 digits)
            if not clean_card.isdigit():
                raise serializers.ValidationError("Card number must contain only digits")
            
            if len(clean_card) < 13 or len(clean_card) > 19:
                raise serializers.ValidationError("Card number must be between 13 and 19 digits")
        
        return value
    
    def validate(self, data):
        """
        Validate that either basket or amount is provided, but when basket is provided,
        amount will be calculated automatically.
        """
        basket = data.get('basket')
        amount = data.get('amount')
        
        if basket:
            # If basket is provided, amount will be set automatically from basket total
            # Remove amount from validation since it will be overridden
            if 'amount' in data:
                del data['amount']
        elif not amount:
            # If no basket is provided, amount is required
            raise serializers.ValidationError("Either 'basket' or 'amount' must be provided.")
        
        return data
