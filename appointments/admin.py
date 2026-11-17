from django.contrib import admin
from .models import ViewingRequest

class ViewingRequestAdmin(admin.ModelAdmin):
    list_display = ['car', 'buyer', 'seller', 'preferred_date', 'preferred_time', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'preferred_date']
    search_fields = ['car__title', 'buyer__username', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('car', 'buyer', 'seller', 'preferred_date', 'preferred_time', 'message')
        }),
        ('Status', {
            'fields': ('status', 'response_message', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(ViewingRequest, ViewingRequestAdmin)