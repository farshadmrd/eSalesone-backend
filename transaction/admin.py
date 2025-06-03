from django.contrib import admin
from .models import Transaction, Basket, BasketItem

class BasketItemInline(admin.TabularInline):
    """
    Inline admin for basket items.
    """
    model = BasketItem
    extra = 1
    fields = ['service_type', 'quantity']
    readonly_fields = []

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """
    Admin configuration for Basket model.
    """
    list_display = ['id', 'items_summary', 'total_amount', 'tax_amount', 'final_total', 'status', 'has_transaction', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at', 'total_amount', 'tax_amount', 'final_total', 'items_summary', 'transaction_info']
    ordering = ['-created_at']
    inlines = [BasketItemInline]
    actions = ['recalculate_totals']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'status', 'created_at')
        }),
        ('Items Summary', {
            'fields': ('items_summary',)
        }),
        ('Totals', {
            'fields': ('total_amount', 'tax_amount', 'final_total')
        }),
        ('Transaction Information', {
            'fields': ('transaction_info',),
            'classes': ('collapse',)
        })
    )
    
    def items_summary(self, obj):
        """Display a summary of items in the basket."""
        items = []
        for item in obj.items.all():
            items.append(f"{item.service_type} x{item.quantity}")
        return ", ".join(items) if items else "No items"
    items_summary.short_description = 'Items'
    
    def final_total(self, obj):
        """Display the final total including tax."""
        return f"${obj.total_amount + obj.tax_amount}"
    final_total.short_description = 'Final Total (with tax)'
    
    def has_transaction(self, obj):
        """Check if basket has associated transactions."""
        return obj.transactions.exists()
    has_transaction.boolean = True
    has_transaction.short_description = 'Has Transaction'
    
    def transaction_info(self, obj):
        """Display information about associated transactions."""
        transactions = obj.transactions.all()
        if transactions:
            info = []
            for trans in transactions:
                info.append(f"Transaction {trans.id[:8]}... - {trans.status} - ${trans.amount}")
            return "\n".join(info)
        return "No transactions"
    transaction_info.short_description = 'Associated Transactions'
    
    def recalculate_totals(self, request, queryset):
        """Admin action to recalculate totals for selected baskets."""
        updated = 0
        for basket in queryset:
            basket.update_totals()
            updated += 1
        self.message_user(request, f'Successfully recalculated totals for {updated} baskets.')
    recalculate_totals.short_description = "Recalculate totals for selected baskets"

@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for BasketItem model.
    """
    list_display = ['id', 'basket_short_id', 'service_type', 'quantity', 'unit_price', 'get_total_price', 'created_at']
    list_filter = ['created_at', 'service_type', 'basket__status']
    readonly_fields = ['id', 'created_at', 'get_total_price', 'unit_price']
    ordering = ['-created_at']
    search_fields = ['basket__id', 'service_type__name', 'service_type__service__title']
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'
    
    def unit_price(self, obj):
        """Display the unit price of the service type."""
        return f"${obj.service_type.price}"
    unit_price.short_description = 'Unit Price'
    
    def basket_short_id(self, obj):
        """Display a shortened basket ID for better readability."""
        return f"{str(obj.basket.id)[:8]}..."
    basket_short_id.short_description = 'Basket'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Transaction model.
    """
    list_display = ['id', 'full_name', 'email', 'amount', 'basket_total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'description', 'basket__id']
    readonly_fields = ['id', 'created_at', 'basket_total', 'basket_tax', 'basket_items_display']
    ordering = ['-created_at']
    actions = ['set_amount_from_basket']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'basket', 'status', 'amount', 'description')
        }),
        ('Basket Information', {
            'fields': ('basket_items_display', 'basket_total', 'basket_tax'),
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
    
    def basket_total(self, obj):
        """Display basket total amount including tax."""
        if obj.basket:
            total_with_tax = obj.basket.total_amount + obj.basket.tax_amount
            return f"${total_with_tax} (${obj.basket.total_amount} + ${obj.basket.tax_amount} tax)"
        return "No basket"
    basket_total.short_description = 'Basket Total (with tax)'
    
    def basket_tax(self, obj):
        """Display basket tax amount."""
        if obj.basket:
            return f"${obj.basket.tax_amount}"
        return "No basket"
    basket_tax.short_description = 'Tax Amount'
    
    def basket_items_display(self, obj):
        """Display basket items in a readable format."""
        if obj.basket:
            items = []
            for item in obj.basket.items.all():
                items.append(f"{item.service_type} x{item.quantity} (${item.get_total_price()})")
            return "\n".join(items) if items else "No items"
        return "No basket"
    basket_items_display.short_description = 'Basket Items'
    
    def set_amount_from_basket(self, request, queryset):
        """Admin action to set transaction amount from basket total."""
        updated = 0
        for transaction in queryset:
            if transaction.basket:
                old_amount = transaction.amount
                transaction.set_amount_from_basket()
                transaction.save()
                updated += 1
        self.message_user(request, f'Successfully updated amounts for {updated} transactions from their baskets.')
    set_amount_from_basket.short_description = "Set amount from basket total for selected transactions"
