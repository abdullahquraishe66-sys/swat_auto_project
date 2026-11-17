from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from cars.models import Car
from .models import ViewingRequest
from .forms import ViewingRequestForm, ResponseForm

@login_required
def request_viewing(request, car_id):
    """Request a viewing for a car"""
    car = get_object_or_404(Car, pk=car_id)
    
    # Check if car is available for viewing
    if car.status != 'approved':
        messages.error(request, 'This car is not available for viewing.')
        return redirect('cars:detail', pk=car.id)
    
    # Can't request viewing for your own car
    if car.seller == request.user:
        messages.warning(request, 'You cannot request a viewing for your own car.')
        return redirect('cars:detail', pk=car.id)
    
    if request.method == 'POST':
        form = ViewingRequestForm(request.POST)
        if form.is_valid():
            viewing_request = form.save(commit=False)
            viewing_request.car = car
            viewing_request.buyer = request.user
            viewing_request.seller = car.seller
            viewing_request.save()
            
            messages.success(request, f'✅ Viewing request sent to {car.seller.first_name}! They will contact you soon.')
            return redirect('appointments:my_requests')
    else:
        form = ViewingRequestForm()
    
    context = {
        'car': car,
        'form': form,
        'page_title': f'Request Viewing - {car.title}'
    }
    return render(request, 'appointments/request_viewing.html', context)

@login_required
def my_requests(request):
    """View all requests made by the user (as buyer)"""
    requests = ViewingRequest.objects.filter(buyer=request.user).order_by('-created_at')
    
    paginator = Paginator(requests, 10)
    page = request.GET.get('page', 1)
    requests_page = paginator.get_page(page)
    
    context = {
        'requests': requests_page,
        'page_title': 'My Viewing Requests - SWAT AUTO'
    }
    return render(request, 'appointments/my_requests.html', context)

@login_required
def manage_requests(request):
    """Manage incoming viewing requests (as seller)"""
    requests = ViewingRequest.objects.filter(seller=request.user).order_by('-created_at')
    
    # Counts
    total = requests.count()
    pending = requests.filter(status='pending').count()
    accepted = requests.filter(status='accepted').count()
    rejected = requests.filter(status='rejected').count()
    completed = requests.filter(status='completed').count()
    
    paginator = Paginator(requests, 10)
    page = request.GET.get('page', 1)
    requests_page = paginator.get_page(page)
    
    context = {
        'requests': requests_page,
        'total': total,
        'pending': pending,
        'accepted': accepted,
        'rejected': rejected,
        'completed': completed,
        'page_title': 'Manage Viewing Requests - SWAT AUTO'
    }
    return render(request, 'appointments/manage_requests.html', context)

@login_required
def respond_request(request, request_id):
    """Accept or reject a viewing request"""
    viewing_request = get_object_or_404(ViewingRequest, pk=request_id)
    
    # Check if user is the seller
    if viewing_request.seller != request.user:
        messages.error(request, 'You do not have permission to respond to this request.')
        return redirect('appointments:manage_requests')
    
    # Check if already responded
    if viewing_request.status != 'pending':
        messages.warning(request, f'This request has already been {viewing_request.get_status_display().lower()}.')
        return redirect('appointments:manage_requests')
    
    action = request.POST.get('action')
    response_message = request.POST.get('response_message', '')
    
    if action == 'accept':
        viewing_request.accept()
        viewing_request.response_message = response_message
        viewing_request.save()
        messages.success(request, f'✅ Viewing request accepted for {viewing_request.car.title}!')
    elif action == 'reject':
        viewing_request.reject()
        viewing_request.response_message = response_message
        viewing_request.save()
        messages.warning(request, f'❌ Viewing request rejected for {viewing_request.car.title}.')
    else:
        messages.error(request, 'Invalid action.')
    
    return redirect('appointments:manage_requests')

@login_required
def cancel_request(request, request_id):
    """Cancel a viewing request (as buyer)"""
    viewing_request = get_object_or_404(ViewingRequest, pk=request_id)
    
    # Check if user is the buyer
    if viewing_request.buyer != request.user:
        messages.error(request, 'You do not have permission to cancel this request.')
        return redirect('appointments:my_requests')
    
    # Can only cancel pending requests
    if viewing_request.status != 'pending':
        messages.warning(request, f'This request has already been {viewing_request.get_status_display().lower()}.')
        return redirect('appointments:my_requests')
    
    viewing_request.cancel()
    messages.info(request, f'Viewing request for {viewing_request.car.title} cancelled.')
    return redirect('appointments:my_requests')

@login_required
def complete_request(request, request_id):
    """Mark a viewing as completed (as seller)"""
    viewing_request = get_object_or_404(ViewingRequest, pk=request_id)
    
    # Check if user is the seller
    if viewing_request.seller != request.user:
        messages.error(request, 'You do not have permission to complete this request.')
        return redirect('appointments:manage_requests')
    
    # Can only complete accepted requests
    if viewing_request.status != 'accepted':
        messages.warning(request, f'This request must be accepted first.')
        return redirect('appointments:manage_requests')
    
    viewing_request.complete()
    messages.success(request, f'✅ Viewing marked as completed for {viewing_request.car.title}!')
    return redirect('appointments:manage_requests')