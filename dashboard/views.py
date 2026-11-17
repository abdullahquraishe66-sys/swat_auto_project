from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta

from cars.models import Car, Brand
from accounts.models import Profile
from showrooms.models import Showroom
from reports.models import Report
from appointments.models import ViewingRequest
from chat.models import Conversation
from django.contrib.auth.models import User

from .decorators import admin_required


@admin_required
def dashboard_index(request):
    """Main admin dashboard with statistics"""
    # Statistics
    total_users = User.objects.count()
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(status='approved').count()
    pending_cars = Car.objects.filter(status='pending').count()
    sold_cars = Car.objects.filter(status='sold').count()
    total_showrooms = Showroom.objects.filter(is_active=True).count()
    
    # Reports
    pending_reports = Report.objects.filter(status='pending').count()
    total_reports = Report.objects.count()
    
    # Engagement
    total_conversations = Conversation.objects.count()
    total_viewing_requests = ViewingRequest.objects.count()
    pending_viewing_requests = ViewingRequest.objects.filter(status='pending').count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_cars = Car.objects.order_by('-created_at')[:5]
    recent_reports = Report.objects.filter(status='pending').order_by('-created_at')[:5]
    
    # Stats for last 7 days
    last_7_days = []
    for i in range(7):
        date = timezone.now() - timedelta(days=i)
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        new_users = User.objects.filter(date_joined__gte=start, date_joined__lt=end).count()
        new_cars = Car.objects.filter(created_at__gte=start, created_at__lt=end).count()
        
        last_7_days.append({
            'date': start.strftime('%b %d'),
            'users': new_users,
            'cars': new_cars,
        })
    
    last_7_days.reverse()
    
    # Most popular brands
    popular_brands = Brand.objects.annotate(
        car_count=Count('cars')
    ).filter(car_count__gt=0).order_by('-car_count')[:5]
    
    context = {
        'total_users': total_users,
        'total_cars': total_cars,
        'active_cars': active_cars,
        'pending_cars': pending_cars,
        'sold_cars': sold_cars,
        'total_showrooms': total_showrooms,
        'pending_reports': pending_reports,
        'total_reports': total_reports,
        'total_conversations': total_conversations,
        'total_viewing_requests': total_viewing_requests,
        'pending_viewing_requests': pending_viewing_requests,
        'recent_users': recent_users,
        'recent_cars': recent_cars,
        'recent_reports': recent_reports,
        'last_7_days': last_7_days,
        'popular_brands': popular_brands,
        'page_title': 'Admin Dashboard - SWAT AUTO'
    }
    return render(request, 'dashboard/index.html', context)


@admin_required
def user_management(request):
    """Manage users"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query)
        )
    
    # Filter by type
    user_type = request.GET.get('type', '')
    if user_type:
        users = users.filter(profile__user_type=user_type)
    
    # Filter by staff
    staff_filter = request.GET.get('staff', '')
    if staff_filter == 'staff':
        users = users.filter(is_staff=True)
    elif staff_filter == 'regular':
        users = users.filter(is_staff=False)
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'user_type': user_type,
        'staff_filter': staff_filter,
        'page_title': 'User Management - Admin'
    }
    return render(request, 'dashboard/users.html', context)


@admin_required
def toggle_user_status(request, user_id):
    """Activate/deactivate a user"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    user = get_object_or_404(User, pk=user_id)
    
    if user == request.user:
        return JsonResponse({'error': 'You cannot deactivate yourself'}, status=400)
    
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
    })


@admin_required
def toggle_staff_status(request, user_id):
    """Toggle staff status"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Only superusers can change staff status'}, status=403)
    
    user = get_object_or_404(User, pk=user_id)
    
    if user == request.user:
        return JsonResponse({'error': 'You cannot change your own status'}, status=400)
    
    user.is_staff = not user.is_staff
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_staff': user.is_staff,
        'message': f'Staff status {"granted" if user.is_staff else "revoked"}'
    })


@admin_required
def car_management(request):
    """Manage all cars"""
    cars = Car.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(seller__username__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        cars = cars.filter(status=status_filter)
    
    # Filter by featured
    featured_filter = request.GET.get('featured', '')
    if featured_filter == 'yes':
        cars = cars.filter(is_featured=True)
    
    paginator = Paginator(cars, 20)
    page = request.GET.get('page', 1)
    cars_page = paginator.get_page(page)
    
    context = {
        'cars': cars_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'featured_filter': featured_filter,
        'status_choices': Car.STATUS_CHOICES,
        'page_title': 'Car Management - Admin'
    }
    return render(request, 'dashboard/cars.html', context)


@admin_required
def pending_cars(request):
    """Show pending car listings for approval"""
    cars = Car.objects.filter(status='pending').order_by('-created_at')
    
    paginator = Paginator(cars, 20)
    page = request.GET.get('page', 1)
    cars_page = paginator.get_page(page)
    
    context = {
        'cars': cars_page,
        'page_title': 'Pending Cars - Admin'
    }
    return render(request, 'dashboard/pending_cars.html', context)


@admin_required
def approve_car(request, car_id):
    """Approve a car listing"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    car = get_object_or_404(Car, pk=car_id)
    car.status = 'approved'
    car.is_verified = True
    car.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Car "{car.title}" approved successfully'
    })


@admin_required
def reject_car(request, car_id):
    """Reject a car listing"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    car = get_object_or_404(Car, pk=car_id)
    car.status = 'rejected'
    car.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Car "{car.title}" rejected'
    })


@admin_required
def toggle_featured(request, car_id):
    """Toggle featured status"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    car = get_object_or_404(Car, pk=car_id)
    car.is_featured = not car.is_featured
    car.save()
    
    return JsonResponse({
        'success': True,
        'is_featured': car.is_featured,
        'message': f'Car {"featured" if car.is_featured else "unfeatured"} successfully'
    })


@admin_required
def featured_cars(request):
    """Manage featured cars"""
    featured = Car.objects.filter(is_featured=True).order_by('-created_at')
    available = Car.objects.filter(is_featured=False, status='approved').order_by('-created_at')[:20]
    
    context = {
        'featured_cars': featured,
        'available_cars': available,
        'page_title': 'Featured Cars - Admin'
    }
    return render(request, 'dashboard/featured.html', context)


@admin_required
def showroom_management(request):
    """Manage showrooms"""
    showrooms = Showroom.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        showrooms = showrooms.filter(
            Q(name__icontains=search_query) |
            Q(owner__username__icontains=search_query)
        )
    
    # Filter by verification
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'yes':
        showrooms = showrooms.filter(is_verified=True)
    elif verified_filter == 'no':
        showrooms = showrooms.filter(is_verified=False)
    
    paginator = Paginator(showrooms, 20)
    page = request.GET.get('page', 1)
    showrooms_page = paginator.get_page(page)
    
    context = {
        'showrooms': showrooms_page,
        'search_query': search_query,
        'verified_filter': verified_filter,
        'page_title': 'Showroom Management - Admin'
    }
    return render(request, 'dashboard/showrooms.html', context)


@admin_required
def toggle_showroom_verification(request, showroom_id):
    """Toggle showroom verification"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    showroom = get_object_or_404(Showroom, pk=showroom_id)
    showroom.is_verified = not showroom.is_verified
    showroom.verified_at = timezone.now() if showroom.is_verified else None
    showroom.save()
    
    return JsonResponse({
        'success': True,
        'is_verified': showroom.is_verified,
        'message': f'Showroom {"verified" if showroom.is_verified else "unverified"}'
    })


@admin_required
def report_management(request):
    """Manage reports"""
    reports = Report.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        reports = reports.filter(report_type=type_filter)
    
    paginator = Paginator(reports, 20)
    page = request.GET.get('page', 1)
    reports_page = paginator.get_page(page)
    
    context = {
        'reports': reports_page,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'status_choices': Report.STATUS_CHOICES,
        'type_choices': Report.TYPE_CHOICES,
        'page_title': 'Report Management - Admin'
    }
    return render(request, 'dashboard/reports.html', context)


@admin_required
def resolve_report(request, report_id):
    """Resolve a report"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    report = get_object_or_404(Report, pk=report_id)
    action = request.POST.get('action', 'resolve')
    notes = request.POST.get('notes', '')
    
    if action == 'resolve':
        report.resolve(request.user, notes)
        msg = 'Report resolved'
    elif action == 'dismiss':
        report.dismiss(request.user, notes)
        msg = 'Report dismissed'
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    return JsonResponse({
        'success': True,
        'message': msg
    })