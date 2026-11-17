from django.db import models
from django.contrib.auth.models import User
from cars.models import Car
from django.utils import timezone

class Conversation(models.Model):
    """
    A conversation between two users about a specific car
    """
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='conversations')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_conversations')
    last_message = models.TextField(blank=True, null=True)
    last_message_time = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_message_time']
        unique_together = ['car', 'buyer', 'seller']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f"{self.buyer.username} - {self.seller.username} - {self.car.title}"

    def get_other_user(self, user):
        """Get the other participant in the conversation"""
        if user == self.buyer:
            return self.seller
        return self.buyer

    def get_unread_count(self, user):
        """Get unread messages count for a user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def mark_as_read(self, user):
        """Mark all messages as read for a user"""
        self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    def get_last_message(self):
        """Get the last message in the conversation"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """
    Individual message within a conversation
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        self.save()