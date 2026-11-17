from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cars.models import Location

class Showroom(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='showrooms')
    
    # Contact Information
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Location
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='showrooms')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Media
    logo = models.ImageField(upload_to='showrooms/logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='showrooms/covers/', blank=True, null=True)
    
    # Description
    description = models.TextField()
    about = models.TextField(blank=True, null=True, help_text="Detailed information about the showroom")
    
    # Business Hours
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_open_24_7 = models.BooleanField(default=False)
    days_open = models.CharField(max_length=100, default="Monday-Saturday", help_text="e.g., Monday-Saturday or Sunday-Thursday")
    
    # Social Media
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    views_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Showroom'
        verbose_name_plural = 'Showrooms'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_verified', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('showrooms:detail', kwargs={'slug': self.slug})
    
    def get_active_cars(self):
        return self.cars.filter(status='approved').count()
    
    def get_total_cars(self):
        return self.cars.count()
    
    def get_sold_cars(self):
        return self.cars.filter(status='sold').count()
    
    def get_featured_cars(self):
        return self.cars.filter(status='approved', is_featured=True)[:6]
    
    def get_all_cars(self):
        return self.cars.filter(status='approved')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.template.defaultfilters import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)