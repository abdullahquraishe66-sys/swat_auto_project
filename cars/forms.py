from django import forms
from django.core.exceptions import ValidationError
from .models import Car, CarImage, Brand, CarModel, Location

class CarForm(forms.ModelForm):
    """
    Form for creating and editing car listings.
    """
    # Override fields to use custom widgets
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_brand'})
    )
    model = forms.ModelChoiceField(
        queryset=CarModel.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_model'})
    )
    
    class Meta:
        model = Car
        fields = [
            'title', 
            'brand', 
            'model', 
            'year', 
            'price',
            'mileage', 
            'fuel_type', 
            'transmission', 
            'body_type',
            'engine_capacity', 
            'color', 
            'condition',
            'registration_city', 
            'registration_year',
            'location', 
            'address',
            'description', 
            'features',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Toyota Corolla 2022 Excellent Condition'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 2022'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 5800000'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 45000'
            }),
            'engine_capacity': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 1800cc'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., White'
            }),
            'registration_city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Mingora'
            }),
            'registration_year': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 2022'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Full address in Swat'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe your car in detail...'
            }),
            'features': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'e.g., Power Steering, AC, Airbags, ABS'
            }),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'body_type': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If brand is selected, filter models
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = CarModel.objects.filter(brand_id=brand_id, is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.brand:
            self.fields['model'].queryset = CarModel.objects.filter(
                brand=self.instance.brand, 
                is_active=True
            )
        else:
            self.fields['model'].queryset = CarModel.objects.none()
        
        # Add empty labels for select fields
        self.fields['fuel_type'].empty_label = 'Select Fuel Type'
        self.fields['transmission'].empty_label = 'Select Transmission'
        self.fields['body_type'].empty_label = 'Select Body Type'
        self.fields['condition'].empty_label = 'Select Condition'
        self.fields['location'].empty_label = 'Select Location'
        
        # Make fields optional where appropriate
        self.fields['engine_capacity'].required = False
        self.fields['color'].required = False
        self.fields['registration_city'].required = False
        self.fields['registration_year'].required = False
        self.fields['address'].required = False
        self.fields['features'].required = False
    
    def clean_price(self):
        """Validate price is positive"""
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError('Price must be greater than 0.')
        return price
    
    def clean_mileage(self):
        """Validate mileage is non-negative"""
        mileage = self.cleaned_data.get('mileage')
        if mileage and mileage < 0:
            raise ValidationError('Mileage cannot be negative.')
        return mileage
    
    def clean_year(self):
        """Validate year is reasonable"""
        year = self.cleaned_data.get('year')
        if year:
            import datetime
            current_year = datetime.datetime.now().year
            if year < 1900 or year > current_year + 1:
                raise ValidationError(f'Year must be between 1900 and {current_year + 1}.')
        return year


class CarImageForm(forms.ModelForm):
    """
    Form for uploading car images.
    """
    class Meta:
        model = CarImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_image(self):
        """Validate image file type and size"""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must be less than 5MB.')
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f'Only {", ".join(valid_extensions)} formats are allowed.')
        
        return image


class CarImageFormSet(forms.modelformset_factory(
    CarImage,
    form=CarImageForm,
    extra=5,
    max_num=10,
    can_delete=True
)):
    """
    Formset for handling multiple car images.
    """
    pass