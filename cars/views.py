from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from .models import Car, CarImage, Brand, CarModel, Location
from .forms import CarForm
from showrooms.models import Showroom
import os
import json

# ============================================
# PUBLIC VIEWS - Anyone can access
# ============================================

def car_list(request):
    """
    Public car listing page with search, filters, sorting, and pagination.
    Only shows cars with 'approved' status.
    """
    # Start with all approved cars
    cars = Car.objects.filter(status='approved').order_by('-created_at')
    
    # Get filter parameters from URL
    search_query = request.GET.get('q', '').strip()
    brand_id = request.GET.get('brand', '')
    model_id = request.GET.get('model', '')
    location_id = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    year = request.GET.get('year', '')
    fuel_type = request.GET.get('fuel_type', '')
    transmission = request.GET.get('transmission', '')
    body_type = request.GET.get('body_type', '')
    condition = request.GET.get('condition', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # ===== SEARCH FILTER =====
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(model__name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(color__icontains=search_query)
        )
    
    # ===== INDIVIDUAL FILTERS =====
    if brand_id and brand_id.isdigit():
        cars = cars.filter(brand_id=int(brand_id))
    
    if model_id and model_id.isdigit():
        cars = cars.filter(model_id=int(model_id))
    
    if location_id and location_id.isdigit():
        cars = cars.filter(location_id=int(location_id))
    
    if min_price and min_price.isdigit():
        cars = cars.filter(price__gte=int(min_price))
    
    if max_price and max_price.isdigit():
        cars = cars.filter(price__lte=int(max_price))
    
    if year and year.isdigit():
        cars = cars.filter(year=int(year))
    
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    if body_type:
        cars = cars.filter(body_type=body_type)
    
    if condition:
        cars = cars.filter(condition=condition)
    
    # ===== SORTING =====
    sort_mapping = {
        'price_asc': 'price',
        'price_desc': '-price',
        'year_desc': '-year',
        'year_asc': 'year',
        'mileage_asc': 'mileage',
        'mileage_desc': '-mileage',
        'created_desc': '-created_at',
        'created_asc': 'created_at',
        'views_desc': '-views_count',
        'views_asc': 'views_count',
    }
    
    if sort_by in sort_mapping:
        cars = cars.order_by(sort_mapping[sort_by])
    else:
        cars = cars.order_by('-created_at')
    
    # ===== PAGINATION =====
    paginator = Paginator(cars, 12)
    page = request.GET.get('page', 1)
    
    try:
        cars_page = paginator.page(page)
    except PageNotAnInteger:
        cars_page = paginator.page(1)
    except EmptyPage:
        cars_page = paginator.page(paginator.num_pages)
    
    # ===== FILTER OPTIONS =====
    brands = Brand.objects.filter(cars__status='approved').distinct()
    locations = Location.objects.filter(cars__status='approved').distinct()
    years = Car.objects.filter(status='approved').values_list('year', flat=True).distinct().order_by('-year')
    
    # Get selected model if brand is selected
    selected_models = []
    if brand_id and brand_id.isdigit():
        selected_models = CarModel.objects.filter(brand_id=int(brand_id), is_active=True)
    
    context = {
        'cars': cars_page,
        'brands': brands,
        'locations': locations,
        'years': years,
        'selected_models': selected_models,
        'search_query': search_query,
        'selected_brand': brand_id,
        'selected_model': model_id,
        'selected_location': location_id,
        'min_price': min_price,
        'max_price': max_price,
        'selected_year': year,
        'selected_fuel': fuel_type,
        'selected_transmission': transmission,
        'selected_body': body_type,
        'selected_condition': condition,
        'sort_by': sort_by,
        'total_cars': cars.count(),
        'page_title': 'Cars for Sale in Swat - SWAT AUTO',
    }
    
    return render(request, 'cars/list.html', context)


def car_detail(request, pk):
    """
    Public car detail page showing complete car information.
    Allows owners and showroom owners to view their cars even if not approved.
    """
    # Get the car
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        from django.http import Http404
        raise Http404("Car does not exist")
    
    # Check if user can view this car
    if car.status != 'approved':
        # Only allow owner or showroom owner to view if not approved
        if not request.user.is_authenticated:
            messages.warning(request, 'This car is not yet available for public viewing.')
            return redirect('cars:list')
        
        # Check if user is the seller or showroom owner
        is_seller = car.seller == request.user
        is_showroom_owner = (car.seller_type == 'showroom' and car.showroom and car.showroom.owner == request.user)
        is_superuser = request.user.is_superuser
        
        if not (is_seller or is_showroom_owner or is_superuser):
            messages.warning(request, 'This car is not yet available for public viewing.')
            return redirect('cars:list')
    
    # Increment view count (only if not owner)
    if not request.user.is_authenticated or (request.user != car.seller):
        car.views_count += 1
        car.save(update_fields=['views_count'])
    
    # Get related cars (same brand, excluding current)
    related_cars = Car.objects.filter(
        brand=car.brand,
        status='approved'
    ).exclude(pk=car.pk)[:4]
    
    # Get all images
    images = car.images.all()
    
    # Get seller information
    seller = car.seller
    seller_profile = seller.profile if hasattr(seller, 'profile') else None
    
    # Get showroom information if applicable
    showroom = car.showroom if car.seller_type == 'showroom' else None
    
    # Get specifications as a list for display
    specs = [
        {'label': 'Brand', 'value': car.brand.name},
        {'label': 'Model', 'value': car.model.name},
        {'label': 'Year', 'value': car.year},
        {'label': 'Price', 'value': f"PKR {car.price:,.0f}"},
        {'label': 'Mileage', 'value': f"{car.mileage:,} KM"},
        {'label': 'Fuel Type', 'value': car.get_fuel_type_display()},
        {'label': 'Transmission', 'value': car.get_transmission_display()},
        {'label': 'Body Type', 'value': car.get_body_type_display()},
    ]
    
    if car.engine_capacity:
        specs.append({'label': 'Engine Capacity', 'value': car.engine_capacity})
    
    if car.color:
        specs.append({'label': 'Color', 'value': car.color})
    
    specs.append({'label': 'Condition', 'value': car.get_condition_display()})
    
    if car.registration_city:
        specs.append({'label': 'Registration City', 'value': car.registration_city})
    
    if car.registration_year:
        specs.append({'label': 'Registration Year', 'value': car.registration_year})
    
    specs.append({'label': 'Location', 'value': car.get_location_display()})
    
    # Parse features into list
    features_list = []
    if car.features:
        features_list = [f.strip() for f in car.features.split(',') if f.strip()]
    
    context = {
        'car': car,
        'images': images,
        'related_cars': related_cars,
        'seller': seller,
        'seller_profile': seller_profile,
        'showroom': showroom,
        'specs': specs,
        'features_list': features_list,
        'page_title': f'{car.title} - SWAT AUTO',
    }
    
    return render(request, 'cars/detail.html', context)


# ============================================
# SELLER DASHBOARD VIEWS - Login Required
# ============================================

@login_required
def dashboard(request):
    """
    Seller dashboard showing all cars owned by the user with statistics.
    """
    user = request.user
    cars = Car.objects.filter(seller=user).order_by('-created_at')
    
    # Calculate statistics
    total_cars = cars.count()
    active_cars = cars.filter(status='approved').count()
    pending_cars = cars.filter(status='pending').count()
    rejected_cars = cars.filter(status='rejected').count()
    sold_cars = cars.filter(status='sold').count()
    
    # Calculate total views using Sum aggregate
    total_views = cars.aggregate(total=Sum('views_count'))['total'] or 0
    
    # Check if user has a showroom
    has_showroom = Showroom.objects.filter(owner=user).exists()
    
    context = {
        'cars': cars,
        'total_cars': total_cars,
        'active_cars': active_cars,
        'pending_cars': pending_cars,
        'rejected_cars': rejected_cars,
        'sold_cars': sold_cars,
        'total_views': total_views,
        'has_showroom': has_showroom,
        'page_title': 'My Dashboard - SWAT AUTO'
    }
    return render(request, 'cars/dashboard.html', context)


@login_required
def car_create(request):
    """
    Create a new car listing with image upload.
    Showroom cars are auto-approved, individual cars need admin approval.
    """
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            
            # Check if user is a showroom owner
            try:
                showroom = Showroom.objects.get(owner=request.user)
                # If user has a showroom, auto-approve
                car.seller_type = 'showroom'
                car.showroom = showroom
                car.status = 'approved'  # Auto-approved!
                car.is_verified = True
                messages.success(request, '✅ Your car has been listed successfully in your showroom and is now visible to buyers!')
            except Showroom.DoesNotExist:
                # Individual seller - needs admin approval
                car.seller_type = 'individual'
                car.status = 'pending'
                messages.info(request, 'Your car has been listed successfully! It will be visible after admin approval.')
            
            car.save()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                CarImage.objects.create(
                    car=car,
                    image=image,
                    is_primary=(i == 0),
                    order=i
                )
            
            return redirect('cars:detail', pk=car.pk)
        else:
            # Show all form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = CarForm()
    
    # Check if user has a showroom for the template
    has_showroom = Showroom.objects.filter(owner=request.user).exists()
    
    context = {
        'form': form,
        'has_showroom': has_showroom,
        'page_title': 'List Your Car - SWAT AUTO'
    }
    return render(request, 'cars/create.html', context)


@login_required
def car_edit(request, pk):
    """
    Edit an existing car listing.
    Showroom owners, sellers, and superusers can edit.
    """
    car = get_object_or_404(Car, pk=pk)
    
    # Check permission
    is_owner = car.seller == request.user
    is_showroom_owner = (car.seller_type == 'showroom' and car.showroom and car.showroom.owner == request.user)
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_showroom_owner or is_superuser):
        messages.error(request, 'You do not have permission to edit this car.')
        return redirect('cars:dashboard')
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            
            # If showroom owner or superuser edited, keep it approved
            if is_showroom_owner or is_superuser:
                if car.status == 'pending':
                    car.status = 'approved'
                    car.save()
            
            messages.success(request, 'Your car has been updated successfully!')
            return redirect('cars:detail', pk=car.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = CarForm(instance=car)
    
    context = {
        'form': form,
        'car': car,
        'images': car.images.all(),
        'page_title': 'Edit Car - SWAT AUTO'
    }
    return render(request, 'cars/edit.html', context)


@login_required
def car_delete(request, pk):
    """
    Delete a car listing and all its images.
    Showroom owners, sellers, and superusers can delete.
    """
    car = get_object_or_404(Car, pk=pk)
    
    # Check permission - allow if user is the seller, showroom owner, or superuser
    is_owner = car.seller == request.user
    is_showroom_owner = (car.seller_type == 'showroom' and car.showroom and car.showroom.owner == request.user)
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_showroom_owner or is_superuser):
        messages.error(request, 'You do not have permission to delete this car.')
        return redirect(request.META.get('HTTP_REFERER', 'cars:dashboard'))
    
    # Delete all associated image files
    for image in car.images.all():
        if image.image and os.path.isfile(image.image.path):
            os.remove(image.image.path)
    
    car_title = car.title
    car.delete()
    messages.success(request, f'✅ Car "{car_title}" deleted successfully!')
    
    # Redirect back to where the user came from
    return redirect(request.META.get('HTTP_REFERER', 'cars:dashboard'))


@login_required
def car_mark_sold(request, pk):
    """
    Mark a car as sold.
    Showroom owners, sellers, and superusers can mark as sold.
    """
    car = get_object_or_404(Car, pk=pk)
    
    # Check permission - allow if user is the seller, showroom owner, or superuser
    is_owner = car.seller == request.user
    is_showroom_owner = (car.seller_type == 'showroom' and car.showroom and car.showroom.owner == request.user)
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_showroom_owner or is_superuser):
        messages.error(request, 'You do not have permission to modify this car.')
        return redirect(request.META.get('HTTP_REFERER', 'cars:dashboard'))
    
    car.status = 'sold'
    car.sold_at = timezone.now()
    car.save()
    
    messages.success(request, f'✅ Car "{car.title}" marked as sold successfully!')
    
    # Redirect back to where the user came from
    return redirect(request.META.get('HTTP_REFERER', 'cars:dashboard'))


# ============================================
# SHOWROOM CAR MANAGEMENT (Called from showrooms app)
# ============================================

@login_required
def approve_showroom_car(request, pk):
    """
    Approve a pending car in the showroom (called from showrooms app).
    Only showroom owner can approve their own cars.
    """
    car = get_object_or_404(Car, pk=pk)
    
    # Check if user owns the showroom
    if car.seller_type != 'showroom' or not car.showroom:
        messages.error(request, 'This car is not associated with a showroom.')
        return redirect('cars:dashboard')
    
    if car.showroom.owner != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to approve this car.')
        return redirect('cars:dashboard')
    
    if car.status == 'pending':
        car.status = 'approved'
        car.is_verified = True
        car.save()
        messages.success(request, f'✅ Car "{car.title}" has been approved and is now visible!')
    else:
        messages.warning(request, 'This car is already approved.')
    
    return redirect('showrooms:dashboard')


@login_required
def reject_showroom_car(request, pk):
    """
    Reject a pending car in the showroom (called from showrooms app).
    Only showroom owner can reject their own cars.
    """
    car = get_object_or_404(Car, pk=pk)
    
    # Check if user owns the showroom
    if car.seller_type != 'showroom' or not car.showroom:
        messages.error(request, 'This car is not associated with a showroom.')
        return redirect('cars:dashboard')
    
    if car.showroom.owner != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to reject this car.')
        return redirect('cars:dashboard')
    
    if car.status == 'pending':
        car.status = 'rejected'
        car.save()
        messages.warning(request, f'❌ Car "{car.title}" has been rejected.')
    else:
        messages.warning(request, 'This car cannot be rejected.')
    
    return redirect('showrooms:dashboard')


# ============================================
# AJAX VIEWS - For dynamic content
# ============================================

def load_models(request):
    """
    AJAX view to load car models based on selected brand.
    Used in the car creation form.
    """
    brand_id = request.GET.get('brand_id')
    if brand_id and brand_id.isdigit():
        models = CarModel.objects.filter(brand_id=int(brand_id), is_active=True)
        data = [{'id': model.id, 'name': model.name} for model in models]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


@login_required
def delete_image(request, pk):
    """
    AJAX view to delete a car image.
    Only the car owner, showroom owner, or superuser can delete images.
    """
    image = get_object_or_404(CarImage, pk=pk)
    car = image.car
    
    # Check permission
    is_owner = car.seller == request.user
    is_showroom_owner = (car.seller_type == 'showroom' and car.showroom and car.showroom.owner == request.user)
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_showroom_owner or is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        # Delete the image file
        if image.image and os.path.isfile(image.image.path):
            os.remove(image.image.path)
        
        image.delete()
        
        # If the deleted image was primary, set another as primary
        if not car.images.filter(is_primary=True).exists():
            first_image = car.images.first()
            if first_image:
                first_image.is_primary = True
                first_image.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ============================================
# HELPER FUNCTIONS
# ============================================

def can_manage_car(user, car):
    """
    Helper function to check if a user can manage (edit/delete/sold) a car.
    Returns True if user is the seller, showroom owner, or superuser.
    """
    if not user.is_authenticated:
        return False
    
    # Superuser can manage anything
    if user.is_superuser:
        return True
    
    # User is the seller
    if car.seller == user:
        return True
    
    # User is the showroom owner
    if car.seller_type == 'showroom' and car.showroom:
        return car.showroom.owner == user
    
    return False


def can_approve_car(user, car):
    """
    Helper function to check if a user can approve a car.
    Returns True if user is the showroom owner or superuser.
    """
    if not user.is_authenticated:
        return False
    
    # Superuser can approve anything
    if user.is_superuser:
        return True
    
    # Showroom owner can approve their own cars
    if car.seller_type == 'showroom' and car.showroom:
        return car.showroom.owner == user
    
    return False


def get_user_cars(user):
    """
    Helper function to get all cars a user can manage.
    Includes cars they own and cars in their showroom.
    """
    if not user.is_authenticated:
        return Car.objects.none()
    
    # Get cars owned by user
    cars = Car.objects.filter(seller=user)
    
    # Get cars in user's showroom (if they have one)
    try:
        showroom = Showroom.objects.get(owner=user)
        cars = cars | showroom.cars.all()
    except Showroom.DoesNotExist:
        pass
    
    return cars.distinct()