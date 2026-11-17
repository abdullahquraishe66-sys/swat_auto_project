from django import forms
from .models import Showroom
from cars.models import Location

class ShowroomForm(forms.ModelForm):
    class Meta:
        model = Showroom
        fields = [
            'name', 'phone', 'whatsapp', 'email',
            'address', 'location',
            'logo', 'cover_image',
            'description', 'about',
            'opening_time', 'closing_time', 'is_open_24_7', 'days_open',
            'facebook', 'instagram', 'youtube', 'twitter', 'website',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter showroom name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 0300-1234567'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 0300-1234567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full address'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short description of your showroom'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed information about your showroom'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_open_24_7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'days_open': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Monday-Saturday'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/yourpage'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/yourpage'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/yourchannel'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/yourpage'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourwebsite.com'}),
        }