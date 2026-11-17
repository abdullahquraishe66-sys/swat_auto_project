from django.urls import path
from . import views

app_name = 'showrooms'

urlpatterns = [
    # ============================================
    # PUBLIC VIEWS - ORDER MATTERS!
    # ============================================
    
    # List page - MUST COME FIRST
    path('', views.showroom_list, name='list'),
    
    # ============================================
    # SHOWROOM OWNER VIEWS - MUST COME BEFORE DETAIL
    # ============================================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_showroom, name='create'),
    path('edit/', views.edit_showroom, name='edit'),
    path('cars/', views.showroom_cars, name='cars'),
    path('add-car/<int:car_id>/', views.add_car_to_showroom, name='add_car'),
    path('remove-car/<int:car_id>/', views.remove_car_from_showroom, name='remove_car'),
    
    # Approve/Reject car
    path('approve-car/<int:car_id>/', views.approve_car, name='approve_car'),
    path('reject-car/<int:car_id>/', views.reject_car, name='reject_car'),
    
    # ============================================
    # DETAIL PAGE - MUST COME LAST
    # ============================================
    path('<slug:slug>/', views.showroom_detail, name='detail'),
]