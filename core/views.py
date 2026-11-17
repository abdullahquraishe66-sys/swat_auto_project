from django.shortcuts import render
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.models import User

# Import models
from cars.models import Car, Brand, Location, CarModel
from showrooms.models import Showroom
from accounts.models import Profile

def index(request):
    """Homepage view with dynamic statistics and search data"""
    
    # --- Homepage Data ---
    featured_cars = Car.objects.filter(status='approved', is_featured=True)[:6]
    latest_cars = Car.objects.filter(status='approved').order_by('-created_at')[:8]
    
    total_cars = Car.objects.filter(status='approved').count()
    total_showrooms = Showroom.objects.filter(is_verified=True, is_active=True).count()
    trusted_sellers = Car.objects.filter(status='approved').values('seller').distinct().count()
    happy_buyers = Profile.objects.filter(user_type='buyer').count()
    if happy_buyers == 0:
        happy_buyers = User.objects.count()
        
    popular_brands = Brand.objects.annotate(car_count=Count('cars')).filter(car_count__gt=0).order_by('-car_count')[:6]
    
    # --- Search Bar Data ---
    # Get only brands that have approved cars
    search_brands = Brand.objects.filter(cars__status='approved').distinct().order_by('name')
    
    # Get only locations that have approved cars
    search_locations = Location.objects.filter(cars__status='approved').distinct().order_by('name')
    
    # Get distinct years from approved cars, sorted descending
    search_years = Car.objects.filter(status='approved').values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'featured_cars': featured_cars,
        'latest_cars': latest_cars,
        'total_cars': total_cars,
        'total_showrooms': total_showrooms,
        'trusted_sellers': trusted_sellers,
        'happy_buyers': happy_buyers,
        'popular_brands': popular_brands,
        'search_brands': search_brands,
        'search_locations': search_locations,
        'search_years': search_years,
        'page_title': 'SWAT AUTO - Find Your Dream Car in Swat',
    }
    return render(request, 'core/index.html', context)

# ... (keep your about, contact, and handler functions below)


def about(request):
    """About us page"""
    total_cars = Car.objects.filter(status='approved').count()
    total_showrooms = Showroom.objects.filter(is_verified=True).count()
    
    context = {
        'total_cars': total_cars,
        'total_showrooms': total_showrooms,
        'total_users': User.objects.count(),
        'page_title': 'About Us - SWAT AUTO',
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """Contact us page with form handling"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        
        # Validate
        if not all([name, email, subject, message_text]):
            messages.error(request, 'Please fill in all required fields.')
        else:
            try:
                # Send email (optional - configure in settings)
                full_message = f"""
New contact message from SWAT AUTO:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message_text}
                """
                
                # Uncomment when email is configured
                # send_mail(
                #     f'Contact Form: {subject}',
                #     full_message,
                #     settings.DEFAULT_FROM_EMAIL,
                #     ['info@swatauto.com'],
                #     fail_silently=True,
                # )
                
                messages.success(request, f'Thank you {name}! Your message has been sent. We will get back to you soon.')
                return render(request, 'core/contact.html', {'page_title': 'Contact Us - SWAT AUTO'})
            except Exception as e:
                messages.error(request, 'Could not send message. Please try again.')
    
    context = {
        'page_title': 'Contact Us - SWAT AUTO',
    }
    return render(request, 'core/contact.html', context)


def handler404(request, exception):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)


def handler403(request, exception):
    """Custom 403 error page"""
    return render(request, '403.html', status=403)


def handler500(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)