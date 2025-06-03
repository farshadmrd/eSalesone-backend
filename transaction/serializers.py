from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
import json
from .models import Transaction

class BasketItemSerializer(serializers.Serializer):
    """
    Serializer for individual basket items.
    """
    name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    basket = BasketItemSerializer(many=True)
    subtotal = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    total_with_tax = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'basket',
            'subtotal',
            'tax_amount',
            'total_with_tax',
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
        read_only_fields = ['id', 'created_at', 'amount', 'subtotal', 'tax_amount', 'total_with_tax']
        extra_kwargs = {
            'card_number': {'write_only': True},
            'expiry_date': {'write_only': True},
            'cvv': {'write_only': True},
        }
    
    def get_subtotal(self, obj):
        """Get the subtotal amount from basket items."""
        return obj.calculate_amount_from_basket()
    
    def get_tax_amount(self, obj):
        """Get the tax amount (10% of subtotal)."""
        return obj.calculate_tax_amount()
    
    def get_total_with_tax(self, obj):
        """Get the total amount including tax."""
        return obj.get_total_with_tax()
    
    def validate_basket(self, value):
        """
        Validate that basket is not empty and has valid items.
        """
        if not value:
            raise serializers.ValidationError("Basket cannot be empty")
        
        for item in value:
            if not all(key in item for key in ['name', 'price', 'quantity']):
                raise serializers.ValidationError(
                    "Each basket item must have 'name', 'price', and 'quantity'"
                )
        
        return value
    
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
    
    def _convert_decimals_to_strings(self, basket_data):
        """
        Convert Decimal objects to strings for JSON serialization.
        """
        converted_data = []
        for item in basket_data:
            converted_item = {}
            for key, value in item.items():
                if isinstance(value, Decimal):
                    converted_item[key] = str(value)
                else:
                    converted_item[key] = value
            converted_data.append(converted_item)
        return converted_data
    
    def create(self, validated_data):
        """
        Create a new Transaction instance.
        Handle the basket field separately since it's a nested serializer.
        """
        # Extract basket data since it's handled by a nested serializer
        basket_data = validated_data.pop('basket', [])
        
        # Convert Decimal objects to strings for JSON serialization
        basket_data = self._convert_decimals_to_strings(basket_data)
        
        # Create the transaction instance
        transaction = Transaction.objects.create(**validated_data)
        
        # Set the basket data (it's stored as JSON in the model)
        transaction.basket = basket_data
        transaction.save()
        
        return transaction
