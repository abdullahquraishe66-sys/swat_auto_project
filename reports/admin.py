from django.contrib import admin
from django.utils.html import format_html
from .models import Report


class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'report_type', 'reporter', 'reason', 'status', 'created_at', 'review_status']
    list_filter = ['report_type', 'reason', 'status', 'created_at']
    search_fields = ['reporter__username', 'description', 'reported_car__title']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('reporter', 'report_type', 'reason', 'description')
        }),
        ('Reported Item', {
            'fields': ('reported_car', 'reported_user', 'reported_showroom')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_under_review', 'mark_resolved', 'mark_dismissed']
    
    def review_status(self, obj):
        if obj.reviewed_by:
            return format_html(
                '<span style="color: green;">✓ Reviewed by {}</span>',
                obj.reviewed_by.username
            )
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    review_status.short_description = 'Review Status'
    
    @admin.action(description='Mark selected reports as Under Review')
    def mark_under_review(self, request, queryset):
        updated = queryset.update(status=Report.REVIEWED, reviewed_by=request.user)
        self.message_user(request, f'{updated} reports marked as Under Review.')
    
    @admin.action(description='Mark selected reports as Resolved')
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=Report.RESOLVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as Resolved.')
    
    @admin.action(description='Mark selected reports as Dismissed')
    def mark_dismissed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=Report.DISMISSED,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as Dismissed.')


admin.site.register(Report, ReportAdmin)