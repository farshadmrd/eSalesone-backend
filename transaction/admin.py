from django.contrib import admin
from .models import Transaction
import json


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Transaction model.
    """
    list_display = ['short_id', 'full_name', 'email', 'amount', 'basket_subtotal', 'basket_tax', 'total_with_tax', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'description', 'id']
    readonly_fields = ['id', 'created_at', 'basket_subtotal', 'basket_tax', 'total_with_tax', 'basket_items_display']
    ordering = ['-created_at']
    actions = ['recalculate_amount_from_basket', 'mark_completed', 'mark_failed']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'status', 'amount', 'description')
        }),
        ('Basket Information', {
            'fields': ('basket', 'basket_items_display', 'basket_subtotal', 'basket_tax', 'total_with_tax'),
            'classes': ('collapse',)
        }),
        ('Customer Information', {
            'fields': ('full_name', 'email', 'phone_number')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Payment Information', {
            'fields': ('card_number', 'expiry_date', 'cvv'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def short_id(self, obj):
        """Display a shortened transaction ID for better readability."""
        return f"{str(obj.id)[:8]}..."
    short_id.short_description = 'ID'
    
    def basket_subtotal(self, obj):
        """Display basket subtotal amount (without tax)."""
        subtotal = obj.calculate_amount_from_basket()
        return f"${subtotal:.2f}"
    basket_subtotal.short_description = 'Subtotal'
    
    def basket_tax(self, obj):
        """Display basket tax amount."""
        tax = obj.calculate_tax_amount()
        return f"${tax:.2f}"
    basket_tax.short_description = 'Tax (10%)'
    
    def total_with_tax(self, obj):
        """Display total amount including tax."""
        total = obj.get_total_with_tax()
        return f"${total:.2f}"
    total_with_tax.short_description = 'Total (with tax)'
    
    def basket_items_display(self, obj):
        """Display basket items in a readable format."""
        if obj.basket:
            try:
                if isinstance(obj.basket, str):
                    basket_data = json.loads(obj.basket)
                else:
                    basket_data = obj.basket
                
                if isinstance(basket_data, list) and basket_data:
                    items = []
                    for item in basket_data:
                        name = item.get('name', 'Unknown Item')
                        price = item.get('price', 0)
                        quantity = item.get('quantity', 1)
                        total = float(price) * int(quantity)
                        items.append(f"{name} - ${price} x {quantity} = ${total:.2f}")
                    return "\n".join(items)
                else:
                    return "No items in basket"
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                return f"Error parsing basket data: {str(e)}"
        return "No basket data"
    basket_items_display.short_description = 'Basket Items'
    
    def recalculate_amount_from_basket(self, request, queryset):
        """Admin action to recalculate transaction amount from basket."""
        updated = 0
        for transaction in queryset:
            old_amount = transaction.amount
            new_amount = transaction.get_total_with_tax()
            transaction.amount = float(new_amount)
            transaction.save()
            updated += 1
        self.message_user(request, f'Successfully recalculated amounts for {updated} transactions. Amounts updated from basket totals.')
    recalculate_amount_from_basket.short_description = "Recalculate amount from basket for selected transactions"
    
    def mark_completed(self, request, queryset):
        """Admin action to mark transactions as completed."""
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'Successfully marked {updated} transactions as COMPLETED.')
    mark_completed.short_description = "Mark selected transactions as COMPLETED"
    
    def mark_failed(self, request, queryset):
        """Admin action to mark transactions as failed."""
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'Successfully marked {updated} transactions as FAILED.')
    mark_failed.short_description = "Mark selected transactions as FAILED"
