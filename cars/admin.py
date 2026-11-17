from django.contrib import admin
from .models import Brand, CarModel, Location, Car, CarImage

class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'is_active']
    list_filter = ['brand', 'is_active']
    search_fields = ['name', 'brand__name']

class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'tehsil', 'is_active']
    list_filter = ['district', 'is_active']
    search_fields = ['name', 'district', 'tehsil']

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 3
    fields = ['image', 'is_primary', 'order', 'caption']

class CarAdmin(admin.ModelAdmin):
    list_display = ['title', 'brand', 'model', 'year', 'price', 'location', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'fuel_type', 'transmission', 'body_type', 'condition', 'year', 'brand']
    search_fields = ['title', 'brand__name', 'model__name', 'description']
    list_editable = ['status', 'is_featured']
    inlines = [CarImageInline]
    readonly_fields = ['views_count', 'favorites_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'brand', 'model', 'year', 'price', 'status', 'is_featured', 'is_verified')
        }),
        ('Vehicle Specifications', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'body_type', 'engine_capacity', 'color', 'condition')
        }),
        ('Location', {
            'fields': ('location', 'address', 'registration_city', 'registration_year')
        }),
        ('Description', {
            'fields': ('description', 'features')
        }),
        ('Seller Information', {
            'fields': ('seller', 'seller_type', 'showroom')
        }),
        ('Statistics', {
            'fields': ('views_count', 'favorites_count', 'created_at', 'updated_at', 'sold_at', 'expired_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.seller_id:
            obj.seller = request.user
        super().save_model(request, obj, form, change)

# Register all models with the admin site
admin.site.register(Brand, BrandAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(CarImage)