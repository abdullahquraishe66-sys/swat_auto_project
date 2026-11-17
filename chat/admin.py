from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'created_at']

class ConversationAdmin(admin.ModelAdmin):
    list_display = ['car', 'buyer', 'seller', 'last_message_time', 'created_at']
    list_filter = ['created_at', 'last_message_time']
    search_fields = ['car__title', 'buyer__username', 'seller__username']
    readonly_fields = ['last_message_time', 'created_at', 'updated_at']
    inlines = [MessageInline]

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message)