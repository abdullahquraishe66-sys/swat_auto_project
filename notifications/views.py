from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Notification


@login_required
def notification_list(request):
    """Display all notifications for the logged-in user"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read/unread
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    notifications_page = paginator.get_page(page)
    
    # Counts
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    total_count = Notification.objects.filter(user=request.user).count()
    
    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
        'total_count': total_count,
        'filter_type': filter_type,
        'page_title': 'Notifications - SWAT AUTO'
    }
    return render(request, 'notifications/list.html', context)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': Notification.get_unread_count(request.user)
        })
    
    # Redirect to link if exists
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """AJAX view to get unread count"""
    count = Notification.get_unread_count(request.user)
    return JsonResponse({'count': count})


@login_required
def delete_notification(request, notification_id):
    """Delete a single notification"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': Notification.get_unread_count(request.user)
        })
    
    messages.success(request, 'Notification deleted.')
    return redirect('notifications:list')


@login_required
def clear_all(request):
    """Clear all read notifications"""
    Notification.objects.filter(user=request.user, is_read=True).delete()
    messages.success(request, 'All read notifications cleared.')
    return redirect('notifications:list')