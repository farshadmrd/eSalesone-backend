from django.contrib import admin
from .models import Transaction, Basket


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """
    Admin configuration for Basket model.
    """
    list_display = ['id', 'total_amount', 'tax_amount', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    filter_horizontal = ['services']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Transaction model.
    """
    list_display = ['id', 'full_name', 'email', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'basket', 'status', 'amount', 'description')
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
