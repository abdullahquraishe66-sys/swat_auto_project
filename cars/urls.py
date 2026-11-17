from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    # Public views
    path('', views.car_list, name='list'),
    path('<int:pk>/', views.car_detail, name='detail'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # CRUD Operations
    path('create/', views.car_create, name='create'),
    path('<int:pk>/edit/', views.car_edit, name='edit'),
    path('<int:pk>/delete/', views.car_delete, name='delete'),  # Accepts POST
    path('<int:pk>/mark-sold/', views.car_mark_sold, name='mark_sold'),  # Accepts POST
    
    # AJAX
    path('load-models/', views.load_models, name='load_models'),
    path('delete-image/<int:pk>/', views.delete_image, name='delete_image'),
]