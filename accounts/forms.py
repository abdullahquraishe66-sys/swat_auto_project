from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Profile
from .models import PasswordResetOTP
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your full name'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your phone number (optional)'
    }))
    
    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data.get('email')
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        
        if commit:
            user.save()
            profile = user.profile
            profile.phone = self.cleaned_data.get('phone')
            profile.save()
        
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile including profile picture.
    """
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'readonly': 'readonly'
    }))
    
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'user_type', 'profile_picture']  # ← ADD profile_picture HERE
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def clean_profile_picture(self):
        """Validate profile picture file"""
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (max 2MB)
            if picture.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be less than 2MB.')
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = picture.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(f'Only {", ".join(valid_extensions)} formats are allowed.')
        
        return picture
    
    def save(self, user=None, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        
        if user:
            user.first_name = self.cleaned_data.get('first_name')
            user.last_name = self.cleaned_data.get('last_name')
            user.save()
        
        if commit:
            profile.save()
        
        return profile


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your registered email'
    }))
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email


class VerifyOTPForm(forms.Form):
    otp_code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control text-center fw-bold fs-4',
        'placeholder': '000000',
        'maxlength': '6',
        'style': 'letter-spacing: 10px;'
    }))


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm new password'
    }))
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        
        # Run Django's strong password validators
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
            
        return new_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
            
        return cleaned_data