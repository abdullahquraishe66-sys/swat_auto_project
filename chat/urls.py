from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation'),
    path('start/<int:car_id>/', views.start_conversation, name='start'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('send-ajax/', views.send_ajax_message, name='send_ajax'),
]