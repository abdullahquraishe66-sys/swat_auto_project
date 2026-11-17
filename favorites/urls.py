from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.favorite_list, name='list'),
    path('toggle/', views.toggle_favorite, name='toggle'),
    path('remove/<int:car_id>/', views.remove_favorite, name='remove'),
]