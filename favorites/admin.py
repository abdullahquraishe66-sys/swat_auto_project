from django.contrib import admin
from .models import Favorite

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'car__title']
    readonly_fields = ['created_at']

admin.site.register(Favorite, FavoriteAdmin)