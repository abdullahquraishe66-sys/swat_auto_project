from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cars.models import Car
from .models import Favorite

@login_required
def toggle_favorite(request):
    """Toggle favorite status for a car (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    car_id = request.POST.get('car_id')
    if not car_id:
        return JsonResponse({'error': 'Car ID required'}, status=400)
    
    car = get_object_or_404(Car, pk=car_id)
    
    # Check if already favorited
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        car=car
    )
    
    if not created:
        # If already favorited, remove it
        favorite.delete()
        is_favorited = False
        message = 'Removed from favorites'
    else:
        is_favorited = True
        message = 'Added to favorites'
    
    # Get updated favorite count
    favorites_count = Favorite.objects.filter(user=request.user).count()
    
    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited,
        'message': message,
        'favorites_count': favorites_count
    })

@login_required
def favorite_list(request):
    """Display user's favorite cars"""
    favorites = Favorite.objects.filter(user=request.user).select_related('car')
    
    context = {
        'favorites': favorites,
        'page_title': 'My Favorites - SWAT AUTO'
    }
    return render(request, 'favorites/index.html', context)

@login_required
def remove_favorite(request, car_id):
    """Remove a car from favorites (non-AJAX fallback)"""
    favorite = get_object_or_404(Favorite, user=request.user, car_id=car_id)
    favorite.delete()
    messages.success(request, 'Car removed from favorites')
    return redirect('favorites:list')