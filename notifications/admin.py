from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    list_editable = ['is_read']
    
    fieldsets = (
        ('Recipient', {
            'fields': ('user', 'sender')
        }),
        ('Notification', {
            'fields': ('notification_type', 'title', 'message', 'link')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Notification, NotificationAdmin)