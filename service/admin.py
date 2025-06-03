from django.contrib import admin
from .models import Service, Type

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title', 'description')
    list_filter = ('is_active',)

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'price', 'is_active', 'recommended')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'recommended', 'service')
