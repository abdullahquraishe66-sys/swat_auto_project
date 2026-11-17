from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Profile

class Brand(models.Model):
    """Car manufacturer brand"""
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'


class CarModel(models.Model):
    """Specific car model under a brand"""
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    year_start = models.IntegerField(null=True, blank=True)
    year_end = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    class Meta:
        ordering = ['brand__name', 'name']
        verbose_name = 'Car Model'
        verbose_name_plural = 'Car Models'
        unique_together = ['brand', 'name']


class Location(models.Model):
    """Location in Swat region"""
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100, default='Swat')
    tehsil = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'


class Car(models.Model):
    """Main Car Listing Model"""
    
    # ============================================
    # CHOICE FIELDS (Enum-like options)
    # ============================================
    
    # Fuel Types
    PETROL = 'petrol'
    DIESEL = 'diesel'
    CNG = 'cng'
    ELECTRIC = 'electric'
    HYBRID = 'hybrid'
    
    FUEL_CHOICES = [
        (PETROL, 'Petrol'),
        (DIESEL, 'Diesel'),
        (CNG, 'CNG'),
        (ELECTRIC, 'Electric'),
        (HYBRID, 'Hybrid'),
    ]
    
    # Transmission Types
    MANUAL = 'manual'
    AUTOMATIC = 'automatic'
    CVT = 'cvt'
    
    TRANSMISSION_CHOICES = [
        (MANUAL, 'Manual'),
        (AUTOMATIC, 'Automatic'),
        (CVT, 'CVT'),
    ]
    
    # Body Types
    SEDAN = 'sedan'
    SUV = 'suv'
    HATCHBACK = 'hatchback'
    COUPE = 'coupe'
    CONVERTIBLE = 'convertible'
    PICKUP = 'pickup'
    VAN = 'van'
    TRUCK = 'truck'
    
    BODY_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (HATCHBACK, 'Hatchback'),
        (COUPE, 'Coupe'),
        (CONVERTIBLE, 'Convertible'),
        (PICKUP, 'Pickup'),
        (VAN, 'Van'),
        (TRUCK, 'Truck'),
    ]
    
    # Conditions
    NEW = 'new'
    USED = 'used'
    CERTIFIED = 'certified'
    
    CONDITION_CHOICES = [
        (NEW, 'New'),
        (USED, 'Used'),
        (CERTIFIED, 'Certified Pre-owned'),
    ]
    
    # Listing Status
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SOLD = 'sold'
    EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (SOLD, 'Sold'),
        (EXPIRED, 'Expired'),
    ]
    
    # Seller Types
    INDIVIDUAL = 'individual'
    SHOWROOM = 'showroom'
    
    SELLER_CHOICES = [
        (INDIVIDUAL, 'Individual'),
        (SHOWROOM, 'Showroom'),
    ]
    
    # ============================================
    # BASIC INFORMATION FIELDS
    # ============================================
    
    title = models.CharField(max_length=200)
    """Car listing title (e.g., "Toyota Corolla 2022 Excellent Condition")"""
    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars')
    """Foreign key to Brand model"""
    
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='cars')
    """Foreign key to CarModel model"""
    
    year = models.IntegerField()
    """Manufacturing year (e.g., 2022)"""
    
    price = models.DecimalField(max_digits=15, decimal_places=0)
    """Price in Pakistani Rupees (PKR)"""
    
    # ============================================
    # VEHICLE SPECIFICATIONS
    # ============================================
    
    mileage = models.IntegerField(help_text="Mileage in kilometers")
    """Total kilometers driven"""
    
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    """Fuel type (Petrol, Diesel, CNG, Electric, Hybrid)"""
    
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    """Transmission type (Manual, Automatic, CVT)"""
    
    body_type = models.CharField(max_length=20, choices=BODY_CHOICES)
    """Body type (Sedan, SUV, Hatchback, etc.)"""
    
    engine_capacity = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., 1800cc")
    """Engine capacity (e.g., "1800cc", "2.5L")"""
    
    color = models.CharField(max_length=50, blank=True, null=True)
    """Exterior color (e.g., "White", "Black")"""
    
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default=USED)
    """Car condition (New, Used, Certified Pre-owned)"""
    
    # ============================================
    # REGISTRATION INFORMATION
    # ============================================
    
    registration_city = models.CharField(max_length=100, blank=True, null=True)
    """City where the car is registered"""
    
    registration_year = models.IntegerField(blank=True, null=True)
    """Year the car was first registered"""
    
    # ============================================
    # LOCATION INFORMATION
    # ============================================
    
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='cars')
    """Foreign key to Location model (Swat locations)"""
    
    address = models.TextField(blank=True, null=True)
    """Full address where the car is located"""
    
    # ============================================
    # DESCRIPTION
    # ============================================
    
    description = models.TextField()
    """Detailed description of the car"""
    
    features = models.TextField(blank=True, null=True, help_text="List key features separated by commas")
    """Key features (comma-separated list)"""
    
    # ============================================
    # SELLER INFORMATION
    # ============================================
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    """User who listed the car"""
    
    seller_type = models.CharField(max_length=20, choices=SELLER_CHOICES, default=INDIVIDUAL)
    """Type of seller (Individual or Showroom)"""
    
    showroom = models.ForeignKey('showrooms.Showroom', on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    """Foreign key to Showroom model (if seller_type is 'showroom')"""
    
    # ============================================
    # LISTING STATUS
    # ============================================
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    """Listing status (Pending, Approved, Rejected, Sold, Expired)"""
    
    is_featured = models.BooleanField(default=False)
    """Whether the car is featured on homepage"""
    
    is_verified = models.BooleanField(default=False)
    """Whether the listing is verified by admin or showroom owner"""
    
    # ============================================
    # STATISTICS
    # ============================================
    
    views_count = models.IntegerField(default=0)
    """Number of times the car listing has been viewed"""
    
    favorites_count = models.IntegerField(default=0)
    """Number of times the car has been favorited"""
    
    # ============================================
    # TIMESTAMPS
    # ============================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    """Timestamp when the car was listed"""
    
    updated_at = models.DateTimeField(auto_now=True)
    """Timestamp when the car listing was last updated"""
    
    sold_at = models.DateTimeField(null=True, blank=True)
    """Timestamp when the car was marked as sold"""
    
    expired_at = models.DateTimeField(null=True, blank=True)
    """Timestamp when the listing expired"""
    
    # ============================================
    # METHODS
    # ============================================
    
    def __str__(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cars:detail', kwargs={'pk': self.pk})
    
    def is_available(self):
        return self.status == self.APPROVED
    
    def get_primary_image(self):
        return self.images.filter(is_primary=True).first()
    
    def get_all_images(self):
        return self.images.all()
    
    def get_seller_name(self):
        if self.seller_type == 'showroom' and self.showroom:
            return self.showroom.name
        return self.seller.get_full_name() or self.seller.username
    
    def get_location_display(self):
        if self.location:
            return self.location.name
        return self.address or 'Location not specified'
    
    def needs_approval(self):
        """Check if this car needs admin approval"""
        if self.seller_type == 'showroom' and self.showroom:
            return False
        return self.status == 'pending'
    
    def can_be_approved_by(self, user):
        """Check if a user can approve this car"""
        if user.is_superuser:
            return True
        if self.seller_type == 'showroom' and self.showroom:
            return self.showroom.owner == user
        return False
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['brand', 'model']),
            models.Index(fields=['price']),
            models.Index(fields=['location']),
            models.Index(fields=['created_at']),
        ]


class CarImage(models.Model):
    """Multiple images for a car listing"""
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    """Foreign key to Car model"""
    
    image = models.ImageField(upload_to='cars/')
    """The actual image file"""
    
    is_primary = models.BooleanField(default=False)
    """Whether this is the primary/cover image"""
    
    caption = models.CharField(max_length=200, blank=True, null=True)
    """Optional caption for the image"""
    
    order = models.IntegerField(default=0)
    """Display order of images"""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.car} - Image {self.order}"
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Car Image'
        verbose_name_plural = 'Car Images'
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # If this image is set as primary, unset others
            CarImage.objects.filter(car=self.car, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)