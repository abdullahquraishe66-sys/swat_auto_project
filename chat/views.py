from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from cars.models import Car
from .models import Conversation, Message
from .forms import MessageForm

@login_required
def inbox(request):
    """Display all conversations for the logged-in user"""
    user = request.user
    
    # Get all conversations where user is either buyer or seller
    conversations = Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).order_by('-last_message_time')
    
    # Get unread count for each conversation
    for conv in conversations:
        conv.unread_count = conv.get_unread_count(user)
    
    context = {
        'conversations': conversations,
        'page_title': 'Messages - SWAT AUTO'
    }
    return render(request, 'chat/inbox.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """Display a single conversation with messages"""
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    user = request.user
    
    # Check if user is part of this conversation
    if user != conversation.buyer and user != conversation.seller:
        messages.error(request, 'You do not have permission to view this conversation.')
        return redirect('chat:inbox')
    
    # Mark messages as read
    conversation.mark_as_read(user)
    
    # ============================================================
    # FIX: Changed variable name from 'messages' to 'messages_list'
    # ============================================================
    messages_list = conversation.messages.all()  # ← THIS IS THE CHANGE
    
    # Handle new message
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = user
            message.save()
            
            # Update last message in conversation
            conversation.last_message = message.content
            conversation.save()
            
            return redirect('chat:conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    # Get the other user
    other_user = conversation.get_other_user(user)
    
    context = {
        'conversation': conversation,
        'messages_list': messages_list,  # ← THIS MUST MATCH THE VARIABLE NAME
        'other_user': other_user,
        'form': form,
        'page_title': f'Chat with {other_user.username} - SWAT AUTO'
    }
    return render(request, 'chat/conversation.html', context)


@login_required
def start_conversation(request, car_id):
    """Start a new conversation about a car"""
    car = get_object_or_404(Car, pk=car_id)
    
    # Check if car is approved or user is owner
    if car.status != 'approved' and car.seller != request.user:
        messages.error(request, 'This car is not available for chat.')
        return redirect('cars:detail', pk=car.id)
    
    # Can't chat with yourself
    if car.seller == request.user:
        messages.warning(request, 'You cannot start a conversation with yourself.')
        return redirect('cars:detail', pk=car.id)
    
    # Check if conversation already exists
    conversation, created = Conversation.objects.get_or_create(
        car=car,
        buyer=request.user,
        seller=car.seller
    )
    
    if created:
        messages.success(request, f'Conversation started about "{car.title}"')
    else:
        messages.info(request, f'Continuing conversation about "{car.title}"')
    
    return redirect('chat:conversation', conversation_id=conversation.id)


@login_required
def get_unread_count(request):
    """AJAX view to get unread message count"""
    user = request.user
    
    # Get all conversations where user is participant
    conversations = Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    )
    
    total_unread = 0
    for conv in conversations:
        total_unread += conv.get_unread_count(user)
    
    return JsonResponse({'count': total_unread})


@login_required
def send_ajax_message(request):
    """AJAX view to send a message without page reload"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    conversation_id = request.POST.get('conversation_id')
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    user = request.user
    
    # Check if user is part of this conversation
    if user != conversation.buyer and user != conversation.seller:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        content=content
    )
    
    # Update last message
    conversation.last_message = content
    conversation.save()
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'content': message.content,
        'sender': message.sender.username,
        'created_at': message.created_at.strftime('%I:%M %p'),
        'is_sender': True
    })