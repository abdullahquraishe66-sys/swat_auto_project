from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from chat.models import Message
from appointments.models import ViewingRequest


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create notification when a new message is sent"""
    if created:
        conversation = instance.conversation
        # Notify the other user
        if instance.sender == conversation.buyer:
            recipient = conversation.seller
        else:
            recipient = conversation.buyer
        
        Notification.create_notification(
            user=recipient,
            notification_type=Notification.MESSAGE,
            title=f'New message from {instance.sender.first_name or instance.sender.username}',
            message=instance.content[:100] + ('...' if len(instance.content) > 100 else ''),
            link=f'/chat/{conversation.id}/',
            sender=instance.sender
        )


@receiver(post_save, sender=ViewingRequest)
def create_viewing_request_notification(sender, instance, created, **kwargs):
    """Create notification when a viewing is requested or status changes"""
    if created:
        # New viewing request - notify seller
        Notification.create_notification(
            user=instance.seller,
            notification_type=Notification.VIEWING_REQUEST,
            title=f'New viewing request for {instance.car.title}',
            message=f'{instance.buyer.first_name or instance.buyer.username} wants to view your car on {instance.preferred_date}.',
            link='/appointments/manage/',
            sender=instance.buyer
        )
    else:
        # Status changed - notify buyer
        if instance.status == 'accepted':
            Notification.create_notification(
                user=instance.buyer,
                notification_type=Notification.VIEWING_ACCEPTED,
                title=f'Viewing request accepted!',
                message=f'Your viewing request for {instance.car.title} has been accepted.',
                link='/appointments/my-requests/',
                sender=instance.seller
            )
        elif instance.status == 'rejected':
            Notification.create_notification(
                user=instance.buyer,
                notification_type=Notification.VIEWING_REJECTED,
                title=f'Viewing request rejected',
                message=f'Your viewing request for {instance.car.title} was not accepted.',
                link='/appointments/my-requests/',
                sender=instance.seller
            )
        elif instance.status == 'completed':
            Notification.create_notification(
                user=instance.buyer,
                notification_type=Notification.VIEWING_COMPLETED,
                title=f'Viewing completed',
                message=f'Your viewing of {instance.car.title} has been marked as completed.',
                link='/appointments/my-requests/',
                sender=instance.seller
            )