from django.db import models
from django.contrib.auth.models import User
from cars.models import Car

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'car']  # Prevent duplicate favorites
        ordering = ['-created_at']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
    
    def __str__(self):
        return f"{self.user.username} - {self.car.title}"