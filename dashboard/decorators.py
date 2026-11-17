from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorator to check if the user is an admin/staff member.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied("You don't have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view