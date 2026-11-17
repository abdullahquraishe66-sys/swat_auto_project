from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Buyer views
    path('request/<int:car_id>/', views.request_viewing, name='request_viewing'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
    
    # Seller views
    path('manage/', views.manage_requests, name='manage_requests'),
    path('respond/<int:request_id>/', views.respond_request, name='respond_request'),
    path('complete/<int:request_id>/', views.complete_request, name='complete_request'),
]