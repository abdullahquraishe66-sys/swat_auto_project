from django.contrib import admin
from .models import Showroom

class ShowroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'location', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__email', 'address']
    list_editable = ['is_verified', 'is_active']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'description', 'about')
        }),
        ('Contact Information', {
            'fields': ('phone', 'whatsapp', 'email', 'address', 'location')
        }),
        ('Media', {
            'fields': ('logo', 'cover_image')
        }),
        ('Business Hours', {
            'fields': ('opening_time', 'closing_time', 'is_open_24_7', 'days_open')
        }),
        ('Social Media', {
            'fields': ('facebook', 'instagram', 'youtube', 'twitter', 'website')
        }),
        ('Verification & Status', {
            'fields': ('is_verified', 'is_active', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Showroom, ShowroomAdmin)