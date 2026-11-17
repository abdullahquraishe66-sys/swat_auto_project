from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('users/', views.user_management, name='users'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/toggle-staff/', views.toggle_staff_status, name='toggle_staff_status'),
    path('cars/', views.car_management, name='cars'),
    path('cars/pending/', views.pending_cars, name='pending_cars'),
    path('cars/<int:car_id>/approve/', views.approve_car, name='approve_car'),
    path('cars/<int:car_id>/reject/', views.reject_car, name='reject_car'),
    path('cars/<int:car_id>/toggle-featured/', views.toggle_featured, name='toggle_featured'),
    path('cars/featured/', views.featured_cars, name='featured_cars'),
    path('showrooms/', views.showroom_management, name='showrooms'),
    path('showrooms/<int:showroom_id>/toggle-verification/', views.toggle_showroom_verification, name='toggle_showroom_verification'),
    path('reports/', views.report_management, name='reports'),
    path('reports/<int:report_id>/resolve/', views.resolve_report, name='resolve_report'),
]