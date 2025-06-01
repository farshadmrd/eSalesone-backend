from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from .models import Transaction, Basket


class BasketSerializer(serializers.ModelSerializer):
    """
    Serializer for Basket model.
    """
    services_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Basket
        fields = [
            'id',
            'services',
            'services_count',
            'total_amount',
            'tax_amount',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_services_count(self, obj):
        return obj.services.count()


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    basket_details = BasketSerializer(source='basket', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'basket',
            'basket_details',
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
