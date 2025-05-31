from django.contrib import admin
from .models import Profile, Contact


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_title', 'title', 'id')
    list_filter = ('job_title',)
    search_fields = ('name', 'job_title', 'title')
    readonly_fields = ('id',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name')
        }),
        ('Job Details', {
            'fields': ('job_title', 'job_description'),
            'classes': ('collapse',)
        }),
        ('Profile Content', {
            'fields': ('title', 'description')
        }),
        ('Images', {
            'fields': ('profile_picture', 'secondary_picture'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('id',)
        return self.readonly_fields


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'address', 'id')
    list_filter = ('email',)
    search_fields = ('email', 'phone', 'address')
    readonly_fields = ('id',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('id', 'email', 'phone', 'address')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('id',)
        return self.readonly_fields
