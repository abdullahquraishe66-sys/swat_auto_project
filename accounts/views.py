from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import Profile

def register(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your account has been created successfully.')
            return redirect('core:index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register - SWAT AUTO'
    }
    return render(request, 'accounts/register.html', context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Get user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'accounts/login.html', {'form': form})
            
            # Authenticate with username (email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {user.first_name}!')
                
                # Redirect to next parameter if exists
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('core:index')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login - SWAT AUTO'
    }
    return render(request, 'accounts/login.html', context)

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:index')

@login_required
def profile(request):
    """View and edit user profile"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # IMPORTANT: Pass request.FILES for file uploads
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=user)
        
        if form.is_valid():
            form.save(user=user)
            messages.success(request, '✅ Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = UserProfileForm(instance=profile, user=user)
    
    context = {
        'form': form,
        'user': user,
        'profile': profile,
        'page_title': 'My Profile - SWAT AUTO'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'page_title': 'Change Password - SWAT AUTO'
    }
    return render(request, 'accounts/change_password.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import PasswordResetOTP
from .forms import ForgotPasswordForm, VerifyOTPForm, SetNewPasswordForm

def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('core:index')
        
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)
            
            # Create OTP record
            otp_record = PasswordResetOTP.objects.create(user=user)
            otp_code = otp_record.generate_otp()
            
            # Send Email using the real SMTP settings
            subject = 'SWAT AUTO - Password Reset Code'
            message = f"Hello {user.first_name},\n\nYour password reset code is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nIf you did not request this, please ignore this email."
            
            try:
                send_mail(subject, message, None, [email], fail_silently=False)
                request.session['reset_email'] = email
                messages.success(request, f'A 6-digit verification code has been sent to {email}.')
                return redirect('accounts:verify_otp')
            except Exception as e:
                messages.error(request, 'Failed to send email. Please check your internet or email settings.')
                # print(e) # Uncomment to debug errors in terminal
    else:
        form = ForgotPasswordForm()
        
    return render(request, 'accounts/forgot_password.html', {'form': form, 'page_title': 'Forgot Password'})


def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Please enter your email first.')
        return redirect('accounts:forgot_password')
        
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data.get('otp_code')
            user = User.objects.get(email=email)
            
            otp_record = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
            
            if otp_record and otp_record.otp_code == otp_code and otp_record.is_valid():
                otp_record.is_used = True
                otp_record.save()
                request.session['otp_verified'] = True
                messages.success(request, 'Code verified! Please set your new password.')
                return redirect('accounts:set_new_password')
            else:
                messages.error(request, 'Invalid or expired OTP code. Please try again.')
    else:
        form = VerifyOTPForm()
        
    return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email, 'page_title': 'Verify Code'})


def set_new_password(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    
    if not email or not otp_verified:
        messages.error(request, 'Unauthorized access. Please restart the process.')
        return redirect('accounts:forgot_password')
        
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            del request.session['reset_email']
            del request.session['otp_verified']
            
            messages.success(request, 'Your password has been reset successfully! You can now log in.')
            return redirect('accounts:login')
    else:
        form = SetNewPasswordForm()
        
    return render(request, 'accounts/set_new_password.html', {'form': form, 'page_title': 'Set New Password'})