from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    # Notification types
    MESSAGE = 'message'
    VIEWING_REQUEST = 'viewing_request'
    VIEWING_ACCEPTED = 'viewing_accepted'
    VIEWING_REJECTED = 'viewing_rejected'
    VIEWING_COMPLETED = 'viewing_completed'
    LISTING_APPROVED = 'listing_approved'
    LISTING_REJECTED = 'listing_rejected'
    LISTING_SOLD = 'listing_sold'
    NEW_FAVORITE = 'new_favorite'
    NEW_CAR = 'new_car'
    SHOWROOM_APPROVED = 'showroom_approved'
    
    TYPE_CHOICES = [
        (MESSAGE, 'New Message'),
        (VIEWING_REQUEST, 'Viewing Request'),
        (VIEWING_ACCEPTED, 'Viewing Accepted'),
        (VIEWING_REJECTED, 'Viewing Rejected'),
        (VIEWING_COMPLETED, 'Viewing Completed'),
        (LISTING_APPROVED, 'Listing Approved'),
        (LISTING_REJECTED, 'Listing Rejected'),
        (LISTING_SOLD, 'Listing Sold'),
        (NEW_FAVORITE, 'New Favorite'),
        (NEW_CAR, 'New Car Listed'),
        (SHOWROOM_APPROVED, 'Showroom Approved'),
    ]
    
    # Icon mapping
    TYPE_ICONS = {
        MESSAGE: 'bi-chat-dots-fill',
        VIEWING_REQUEST: 'bi-calendar-check-fill',
        VIEWING_ACCEPTED: 'bi-check-circle-fill',
        VIEWING_REJECTED: 'bi-x-circle-fill',
        VIEWING_COMPLETED: 'bi-check-all',
        LISTING_APPROVED: 'bi-check-circle-fill',
        LISTING_REJECTED: 'bi-x-circle-fill',
        LISTING_SOLD: 'bi-tag-fill',
        NEW_FAVORITE: 'bi-heart-fill',
        NEW_CAR: 'bi-car-front-fill',
        SHOWROOM_APPROVED: 'bi-building-fill-check',
    }
    
    # Color mapping
    TYPE_COLORS = {
        MESSAGE: 'primary',
        VIEWING_REQUEST: 'info',
        VIEWING_ACCEPTED: 'success',
        VIEWING_REJECTED: 'danger',
        VIEWING_COMPLETED: 'success',
        LISTING_APPROVED: 'success',
        LISTING_REJECTED: 'danger',
        LISTING_SOLD: 'warning',
        NEW_FAVORITE: 'danger',
        NEW_CAR: 'primary',
        SHOWROOM_APPROVED: 'success',
    }
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification details
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional link
    link = models.CharField(max_length=500, blank=True, null=True)
    
    # Optional sender (who triggered it)
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sent_notifications'
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark this notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_icon(self):
        """Get the appropriate icon for this notification"""
        return self.TYPE_ICONS.get(self.notification_type, 'bi-bell-fill')
    
    def get_color(self):
        """Get the appropriate color for this notification"""
        return self.TYPE_COLORS.get(self.notification_type, 'secondary')
    
    def time_since(self):
        """Return human-readable time"""
        from django.utils.timesince import timesince
        return timesince(self.created_at)
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, link=None, sender=None):
        """Helper method to create a notification"""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            sender=sender
        )
    
    @classmethod
    def get_unread_count(cls, user):
        """Get unread count for a user"""
        return cls.objects.filter(user=user, is_read=False).count()