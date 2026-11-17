from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('car/<int:car_id>/', views.report_car, name='report_car'),
    path('showroom/<int:showroom_id>/', views.report_showroom, name='report_showroom'),
    path('my-reports/', views.my_reports, name='my_reports'),
]