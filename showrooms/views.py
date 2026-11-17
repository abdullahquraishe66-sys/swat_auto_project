from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.utils import timezone
from django.template.defaultfilters import slugify
from .models import Showroom
from .forms import ShowroomForm
from cars.models import Car
import os

# ============================================
# PUBLIC VIEWS - Anyone can access
# ============================================

def showroom_list(request):
    """Public showroom listing page"""
    showrooms = Showroom.objects.filter(is_active=True).order_by('-is_verified', '-created_at')
    
    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        showrooms = showrooms.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Location filter
    location_id = request.GET.get('location', '')
    if location_id and location_id.isdigit():
        showrooms = showrooms.filter(location_id=int(location_id))
    
    # Pagination
    paginator = Paginator(showrooms, 12)
    page = request.GET.get('page', 1)
    
    try:
        showrooms_page = paginator.page(page)
    except PageNotAnInteger:
        showrooms_page = paginator.page(1)
    except EmptyPage:
        showrooms_page = paginator.page(paginator.num_pages)
    
    context = {
        'showrooms': showrooms_page,
        'search_query': search_query,
        'selected_location': location_id,
        'page_title': 'Showrooms in Swat - SWAT AUTO'
    }
    return render(request, 'showrooms/list.html', context)


def showroom_detail(request, slug):
    """Public showroom detail page"""
    showroom = get_object_or_404(Showroom, slug=slug, is_active=True)
    
    # Increment view count
    showroom.views_count += 1
    showroom.save(update_fields=['views_count'])
    
    # Get cars
    cars = showroom.cars.filter(status='approved').order_by('-created_at')
    featured_cars = cars.filter(is_featured=True)[:6]
    all_cars = cars[:12]
    
    context = {
        'showroom': showroom,
        'featured_cars': featured_cars,
        'cars': all_cars,
        'total_cars': cars.count(),
        'page_title': f'{showroom.name} - SWAT AUTO'
    }
    return render(request, 'showrooms/detail.html', context)


# ============================================
# SHOWROOM OWNER VIEWS (Login Required)
# ============================================

@login_required
def dashboard(request):
    """Showroom owner dashboard with full control"""
    # Check if user has a showroom
    try:
        showroom = Showroom.objects.get(owner=request.user)
    except Showroom.DoesNotExist:
        # If user doesn't have a showroom, redirect to create page
        messages.info(request, 'You need to create a showroom first.')
        return redirect('showrooms:create')
    
    # Get all cars
    cars = showroom.cars.all().order_by('-created_at')
    total_cars = cars.count()
    active_cars = cars.filter(status='approved').count()
    pending_cars = cars.filter(status='pending').count()
    rejected_cars = cars.filter(status='rejected').count()
    sold_cars = cars.filter(status='sold').count()
    
    context = {
        'showroom': showroom,
        'cars': cars[:6],
        'total_cars': total_cars,
        'active_cars': active_cars,
        'pending_cars': pending_cars,
        'rejected_cars': rejected_cars,
        'sold_cars': sold_cars,
        'page_title': 'Showroom Dashboard - SWAT AUTO'
    }
    return render(request, 'showrooms/dashboard.html', context)


@login_required
def create_showroom(request):
    """Create a new showroom"""
    # Check if user already has a showroom
    if Showroom.objects.filter(owner=request.user).exists():
        messages.warning(request, 'You already have a showroom. You can edit it from your dashboard.')
        return redirect('showrooms:dashboard')
    
    if request.method == 'POST':
        form = ShowroomForm(request.POST, request.FILES)
        if form.is_valid():
            showroom = form.save(commit=False)
            showroom.owner = request.user
            showroom.save()
            
            messages.success(request, 'Your showroom has been created successfully! It will be visible after verification.')
            return redirect('showrooms:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = ShowroomForm()
    
    context = {
        'form': form,
        'page_title': 'Create Showroom - SWAT AUTO'
    }
    return render(request, 'showrooms/create.html', context)


@login_required
def edit_showroom(request):
    """Edit showroom profile"""
    showroom = get_object_or_404(Showroom, owner=request.user)
    
    if request.method == 'POST':
        form = ShowroomForm(request.POST, request.FILES, instance=showroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your showroom has been updated successfully!')
            return redirect('showrooms:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = ShowroomForm(instance=showroom)
    
    context = {
        'form': form,
        'showroom': showroom,
        'page_title': 'Edit Showroom - SWAT AUTO'
    }
    return render(request, 'showrooms/edit.html', context)


@login_required
def showroom_cars(request):
    """Manage cars under showroom"""
    showroom = get_object_or_404(Showroom, owner=request.user)
    cars = showroom.cars.all().order_by('-created_at')
    
    context = {
        'showroom': showroom,
        'cars': cars,
        'page_title': 'Manage Showroom Cars - SWAT AUTO'
    }
    return render(request, 'showrooms/cars.html', context)


@login_required
def add_car_to_showroom(request, car_id):
    """Add an existing car to showroom"""
    car = get_object_or_404(Car, pk=car_id, seller=request.user)
    showroom = get_object_or_404(Showroom, owner=request.user)
    
    if car.seller_type == 'individual':
        car.seller_type = 'showroom'
        car.showroom = showroom
        car.status = 'approved'  # Auto-approve for showroom
        car.is_verified = True
        car.save()
        messages.success(request, 'Car added to your showroom successfully!')
        return redirect('cars:detail', pk=car.pk)
    else:
        messages.warning(request, 'This car is already in a showroom.')
        return redirect('showrooms:cars')


@login_required
def remove_car_from_showroom(request, car_id):
    """Remove a car from showroom"""
    car = get_object_or_404(Car, pk=car_id, seller=request.user)
    
    if car.seller_type == 'showroom' and car.showroom and car.showroom.owner == request.user:
        car.seller_type = 'individual'
        car.showroom = None
        car.status = 'pending'  # Needs approval again
        car.save()
        messages.success(request, 'Car removed from showroom successfully!')
    else:
        messages.error(request, 'You cannot remove this car from the showroom.')
    
    return redirect('showrooms:cars')


# ============================================
# SHOWROOM CAR APPROVAL VIEWS
# ============================================

@login_required
def approve_car(request, car_id):
    """Approve a pending car in the showroom"""
    car = get_object_or_404(Car, pk=car_id)
    showroom = get_object_or_404(Showroom, owner=request.user)
    
    # Check if car belongs to this showroom
    if car.showroom != showroom:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        messages.error(request, 'You do not have permission to approve this car.')
        return redirect('showrooms:dashboard')
    
    if car.status == 'pending':
        car.status = 'approved'
        car.is_verified = True
        car.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Car "{car.title}" approved!'})
        
        messages.success(request, f'✅ Car "{car.title}" has been approved and is now visible to buyers!')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Car already approved'}, status=400)
        messages.warning(request, f'This car is already {car.get_status_display()}.')
    
    return redirect('showrooms:dashboard')


@login_required
def reject_car(request, car_id):
    """Reject a pending car in the showroom"""
    car = get_object_or_404(Car, pk=car_id)
    showroom = get_object_or_404(Showroom, owner=request.user)
    
    # Check if car belongs to this showroom
    if car.showroom != showroom:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        messages.error(request, 'You do not have permission to reject this car.')
        return redirect('showrooms:dashboard')
    
    if car.status == 'pending':
        car.status = 'rejected'
        car.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Car "{car.title}" rejected!'})
        
        messages.warning(request, f'❌ Car "{car.title}" has been rejected.')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Cannot reject this car'}, status=400)
        messages.warning(request, f'This car cannot be rejected. Current status: {car.get_status_display()}.')
    
    return redirect('showrooms:dashboard')


# ============================================
# AJAX VIEWS
# ============================================

@login_required
def get_showroom_stats(request):
    """AJAX view to get showroom statistics"""
    try:
        showroom = Showroom.objects.get(owner=request.user)
    except Showroom.DoesNotExist:
        return JsonResponse({'error': 'No showroom found'}, status=404)
    
    cars = showroom.cars.all()
    
    data = {
        'total_cars': cars.count(),
        'active_cars': cars.filter(status='approved').count(),
        'pending_cars': cars.filter(status='pending').count(),
        'sold_cars': cars.filter(status='sold').count(),
        'rejected_cars': cars.filter(status='rejected').count(),
        'total_views': showroom.views_count,
        'is_verified': showroom.is_verified,
    }
    
    return JsonResponse(data)


# ============================================
# HELPER FUNCTIONS
# ============================================

def user_has_showroom(user):
    """Check if a user has a showroom"""
    if not user.is_authenticated:
        return False
    return Showroom.objects.filter(owner=user).exists()


def get_user_showroom(user):
    """Get the showroom for a user"""
    if not user.is_authenticated:
        return None
    try:
        return Showroom.objects.get(owner=user)
    except Showroom.DoesNotExist:
        return None