from django.db import models
from django.contrib.auth.models import User
from cars.models import Car
from showrooms.models import Showroom
from django.utils import timezone


class Report(models.Model):
    # Report types
    CAR = 'car'
    USER = 'user'
    SHOWROOM = 'showroom'
    
    TYPE_CHOICES = [
        (CAR, 'Car Listing'),
        (USER, 'User'),
        (SHOWROOM, 'Showroom'),
    ]
    
    # Report reasons
    FRAUD = 'fraud'
    FAKE_PRICE = 'fake_price'
    WRONG_INFO = 'wrong_info'
    DUPLICATE = 'duplicate'
    INAPPROPRIATE = 'inappropriate'
    ALREADY_SOLD = 'already_sold'
    SPAM = 'spam'
    OTHER = 'other'
    
    REASON_CHOICES = [
        (FRAUD, 'Fraud/Scam'),
        (FAKE_PRICE, 'Fake/Wrong Price'),
        (WRONG_INFO, 'Wrong Information'),
        (DUPLICATE, 'Duplicate Listing'),
        (INAPPROPRIATE, 'Inappropriate Content'),
        (ALREADY_SOLD, 'Car Already Sold'),
        (SPAM, 'Spam'),
        (OTHER, 'Other'),
    ]
    
    # Report status
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    RESOLVED = 'resolved'
    DISMISSED = 'dismissed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending Review'),
        (REVIEWED, 'Under Review'),
        (RESOLVED, 'Resolved'),
        (DISMISSED, 'Dismissed'),
    ]
    
    # Reporter
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    
    # What is being reported
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reported_car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_received')
    reported_showroom = models.ForeignKey(Showroom, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    # Report details
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Admin actions
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['report_type']),
        ]
    
    def __str__(self):
        return f"Report #{self.id} - {self.get_reason_display()} ({self.get_status_display()})"
    
    def get_reported_item(self):
        """Get the actual reported object"""
        if self.report_type == self.CAR:
            return self.reported_car
        elif self.report_type == self.USER:
            return self.reported_user
        elif self.report_type == self.SHOWROOM:
            return self.reported_showroom
        return None
    
    def get_reported_item_name(self):
        """Get the name of the reported item"""
        item = self.get_reported_item()
        if item:
            if self.report_type == self.CAR:
                return item.title
            elif self.report_type == self.USER:
                return item.username
            elif self.report_type == self.SHOWROOM:
                return item.name
        return 'Deleted Item'
    
    def resolve(self, admin_user, notes=''):
        """Mark report as resolved"""
        self.status = self.RESOLVED
        self.admin_notes = notes
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save()
    
    def dismiss(self, admin_user, notes=''):
        """Dismiss report"""
        self.status = self.DISMISSED
        self.admin_notes = notes
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save()
    
    def mark_under_review(self, admin_user):
        """Mark as under review"""
        self.status = self.REVIEWED
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save()