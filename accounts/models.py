from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('buyer', 'Buyer'),
            ('seller', 'Seller'),
            ('showroom', 'Showroom Owner'),
        ],
        default='buyer'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random

# ... (Keep your existing Profile model and signals here) ...

# ADD THIS AT THE BOTTOM:
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP expires after 10 minutes
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() < expiration_time and not self.is_used

    def generate_otp(self):
        # Generate a random 6-digit number
        self.otp_code = str(random.randint(100000, 999999))
        self.save()
        return self.otp_code

    def __str__(self):
        return f"{self.user.email} - {self.otp_code}"