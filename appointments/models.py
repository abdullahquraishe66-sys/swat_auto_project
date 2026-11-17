from django.db import models
from django.contrib.auth.models import User
from cars.models import Car
from django.utils import timezone

class ViewingRequest(models.Model):
    # Status choices
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Relationships
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='viewing_requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewing_requests_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewing_requests_as_seller')
    
    # Request details
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Response
    response_message = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Viewing Request'
        verbose_name_plural = 'Viewing Requests'
    
    def __str__(self):
        return f"{self.buyer.username} - {self.car.title} ({self.get_status_display()})"
    
    def accept(self):
        """Accept the viewing request"""
        self.status = self.ACCEPTED
        self.responded_at = timezone.now()
        self.save()
    
    def reject(self):
        """Reject the viewing request"""
        self.status = self.REJECTED
        self.responded_at = timezone.now()
        self.save()
    
    def complete(self):
        """Mark the viewing as completed"""
        self.status = self.COMPLETED
        self.save()
    
    def cancel(self):
        """Cancel the viewing request"""
        self.status = self.CANCELLED
        self.save()
    
    def get_formatted_date(self):
        """Return formatted date"""
        return self.preferred_date.strftime('%B %d, %Y')
    
    def get_formatted_time(self):
        """Return formatted time"""
        return self.preferred_time.strftime('%I:%M %p')