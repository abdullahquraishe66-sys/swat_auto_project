from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cars.models import Brand, CarModel, Location, Car, CarImage
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import random

class Command(BaseCommand):
    help = 'Seed the database with sample car data for Swat'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@swatauto.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
        
        # Create seller user
        if not User.objects.filter(username='seller@swatauto.com').exists():
            seller = User.objects.create_user(
                username='seller@swatauto.com',
                email='seller@swatauto.com',
                password='seller123',
                first_name='Ahmed'
            )
            seller.profile.phone = '0300-1234567'
            seller.profile.user_type = 'seller'
            seller.profile.save()
            self.stdout.write(self.style.SUCCESS('Created seller: Ahmed'))
        
        # Create brands
        brands_data = [
            {'name': 'Toyota', 'description': 'Japanese automobile manufacturer'},
            {'name': 'Honda', 'description': 'Japanese automobile manufacturer'},
            {'name': 'Suzuki', 'description': 'Japanese automobile manufacturer'},
            {'name': 'KIA', 'description': 'South Korean automobile manufacturer'},
            {'name': 'Hyundai', 'description': 'South Korean automobile manufacturer'},
            {'name': 'Daihatsu', 'description': 'Japanese automobile manufacturer'},
            {'name': 'Nissan', 'description': 'Japanese automobile manufacturer'},
            {'name': 'BMW', 'description': 'German automobile manufacturer'},
            {'name': 'Mercedes-Benz', 'description': 'German automobile manufacturer'},
        ]
        
        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={'description': brand_data['description']}
            )
            brands[brand.name] = brand
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        # Create car models
        models_data = {
            'Toyota': ['Corolla', 'Yaris', 'Vitz', 'Aqua', 'Fortuner', 'Land Cruiser', 'Hilux'],
            'Honda': ['Civic', 'City', 'Accord', 'Vezel', 'CR-V', 'BR-V'],
            'Suzuki': ['Alto', 'Wagon R', 'Cultus', 'Swift', 'Jimny', 'Every'],
            'KIA': ['Sportage', 'Picanto', 'Stonic', 'Telluride'],
            'Hyundai': ['Tucson', 'Santa Fe', 'Elantra', 'Sonata'],
            'Daihatsu': ['Mira', 'Move', 'Tanto'],
            'Nissan': ['Note', 'X-Trail', 'Patrol', 'Sunny'],
            'BMW': ['3 Series', '5 Series', 'X5', 'X3'],
            'Mercedes-Benz': ['C-Class', 'E-Class', 'GLE', 'GLC'],
        }
        
        for brand_name, model_names in models_data.items():
            brand = brands.get(brand_name)
            if brand:
                for model_name in model_names:
                    model, created = CarModel.objects.get_or_create(
                        brand=brand,
                        name=model_name,
                        defaults={'is_active': True}
                    )
                    if created:
                        self.stdout.write(f'Created model: {brand_name} {model_name}')
        
        # Create locations in Swat
        locations_data = [
            {'name': 'Mingora', 'district': 'Swat', 'tehsil': 'Mingora', 'area': 'City Center'},
            {'name': 'Saidu Sharif', 'district': 'Swat', 'tehsil': 'Saidu Sharif', 'area': 'Main Market'},
            {'name': 'Kabal', 'district': 'Swat', 'tehsil': 'Kabal', 'area': 'Bazar'},
            {'name': 'Matta', 'district': 'Swat', 'tehsil': 'Matta', 'area': 'Main Road'},
            {'name': 'Khwazakhela', 'district': 'Swat', 'tehsil': 'Khwazakhela', 'area': 'City Center'},
            {'name': 'Barikot', 'district': 'Swat', 'tehsil': 'Barikot', 'area': 'Main Bazar'},
            {'name': 'Bahrain', 'district': 'Swat', 'tehsil': 'Bahrain', 'area': 'River Side'},
            {'name': 'Kalam', 'district': 'Swat', 'tehsil': 'Kalam', 'area': 'Valley Road'},
            {'name': 'Charbagh', 'district': 'Swat', 'tehsil': 'Charbagh', 'area': 'Main Road'},
            {'name': 'Mingora Surroundings', 'district': 'Swat', 'tehsil': 'Mingora', 'area': 'Outskirts'},
        ]
        
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={
                    'district': loc_data['district'],
                    'tehsil': loc_data['tehsil'],
                    'area': loc_data['area'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created location: {loc_data["name"]}')
        
        # Get seller and locations
        seller = User.objects.get(username='seller@swatauto.com')
        locations = list(Location.objects.all())
        
        # Create sample cars
        car_data = [
            {
                'brand': 'Toyota', 'model': 'Corolla', 'year': 2022, 'price': 5800000,
                'mileage': 45000, 'fuel': 'petrol', 'transmission': 'automatic',
                'body': 'sedan', 'engine': '1800cc', 'color': 'White',
                'condition': 'used', 'title': 'Toyota Corolla 2022 Excellent Condition',
                'description': 'Well-maintained Toyota Corolla with full service history. Perfect family car with great fuel economy.',
                'features': 'Power Steering, AC, Power Windows, Central Locking, Airbags, ABS, Music System, Alloy Rims',
                'location': 'Mingora',
                'address': 'Main Road, Mingora, Swat'
            },
            {
                'brand': 'Honda', 'model': 'Civic', 'year': 2021, 'price': 6200000,
                'mileage': 35000, 'fuel': 'petrol', 'transmission': 'automatic',
                'body': 'sedan', 'engine': '1800cc', 'color': 'Black',
                'condition': 'used', 'title': 'Honda Civic 2021 with Sunroof',
                'description': 'Elegant Honda Civic with sunroof and leather seats. Well-maintained and in excellent condition.',
                'features': 'Sunroof, Leather Seats, Navigation, Bluetooth, USB, Climate Control, Alloy Rims',
                'location': 'Saidu Sharif',
                'address': 'Main Bazar, Saidu Sharif, Swat'
            },
            {
                'brand': 'Suzuki', 'model': 'Alto', 'year': 2023, 'price': 2200000,
                'mileage': 12000, 'fuel': 'petrol', 'transmission': 'manual',
                'body': 'hatchback', 'engine': '660cc', 'color': 'Red',
                'condition': 'new', 'title': 'Suzuki Alto VXL 2023 Brand New',
                'description': 'Brand new Suzuki Alto VXL with dealer warranty. Perfect city car with amazing fuel economy.',
                'features': 'AC, Power Steering, Central Locking, Airbags, ABS, Music System',
                'location': 'Kabal',
                'address': 'Main Bazar, Kabal, Swat'
            },
            {
                'brand': 'Toyota', 'model': 'Fortuner', 'year': 2020, 'price': 18500000,
                'mileage': 28000, 'fuel': 'diesel', 'transmission': 'automatic',
                'body': 'suv', 'engine': '2800cc', 'color': 'Silver',
                'condition': 'used', 'title': 'Toyota Fortuner 4x4 2020',
                'description': 'Powerful Toyota Fortuner with 4x4 capability. Great off-road performance with luxurious interiors.',
                'features': '4x4, Leather Seats, Navigation, Rear Camera, Parking Sensors, Climate Control, Alloy Rims',
                'location': 'Matta',
                'address': 'Main Road, Matta, Swat'
            },
            {
                'brand': 'KIA', 'model': 'Sportage', 'year': 2022, 'price': 7800000,
                'mileage': 22000, 'fuel': 'petrol', 'transmission': 'automatic',
                'body': 'suv', 'engine': '2000cc', 'color': 'Blue',
                'condition': 'used', 'title': 'KIA Sportage 2022 Fully Loaded',
                'description': 'Fully loaded KIA Sportage with all modern features. Excellent condition with low mileage.',
                'features': 'Sunroof, Leather Seats, Navigation, 360 Camera, Parking Sensors, Climate Control, Alloy Rims',
                'location': 'Khwazakhela',
                'address': 'City Center, Khwazakhela, Swat'
            },
            {
                'brand': 'Honda', 'model': 'City', 'year': 2021, 'price': 4500000,
                'mileage': 32000, 'fuel': 'petrol', 'transmission': 'automatic',
                'body': 'sedan', 'engine': '1500cc', 'color': 'White',
                'condition': 'used', 'title': 'Honda City 2021 Aspire',
                'description': 'Well-maintained Honda City Aspire with all standard features. Great value for money.',
                'features': 'AC, Power Windows, Central Locking, Airbags, ABS, Music System, Alloy Rims',
                'location': 'Barikot',
                'address': 'Main Bazar, Barikot, Swat'
            },
            {
                'brand': 'Suzuki', 'model': 'Wagon R', 'year': 2022, 'price': 2800000,
                'mileage': 18000, 'fuel': 'petrol', 'transmission': 'automatic',
                'body': 'hatchback', 'engine': '1000cc', 'color': 'Silver',
                'condition': 'used', 'title': 'Suzuki Wagon R 2022 Automatic',
                'description': 'Spacious Suzuki Wagon R with automatic transmission. Great family car with excellent fuel economy.',
                'features': 'AC, Power Steering, Central Locking, Airbags, ABS, Music System',
                'location': 'Bahrain',
                'address': 'River Side, Bahrain, Swat'
            },
            {
                'brand': 'Toyota', 'model': 'Yaris', 'year': 2022, 'price': 4800000,
                'mileage': 15000, 'fuel': 'petrol', 'transmission': 'automatic',
                'body': 'sedan', 'engine': '1500cc', 'color': 'Black',
                'condition': 'used', 'title': 'Toyota Yaris 2022 Premium',
                'description': 'Well-maintained Toyota Yaris with premium features. Excellent fuel economy and comfort.',
                'features': 'AC, Power Windows, Central Locking, Airbags, ABS, Music System, Alloy Rims',
                'location': 'Kalam',
                'address': 'Valley Road, Kalam, Swat'
            },
        ]
        
        for data in car_data:
            brand = Brand.objects.get(name=data['brand'])
            model = CarModel.objects.get(brand=brand, name=data['model'])
            location = Location.objects.get(name=data['location'])
            
            car = Car.objects.create(
                title=data['title'],
                brand=brand,
                model=model,
                year=data['year'],
                price=data['price'],
                mileage=data['mileage'],
                fuel_type=data['fuel'],
                transmission=data['transmission'],
                body_type=data['body'],
                engine_capacity=data['engine'],
                color=data['color'],
                condition=data['condition'],
                location=location,
                address=data['address'],
                description=data['description'],
                features=data['features'],
                seller=seller,
                seller_type='individual',
                status='approved',
                is_verified=True,
                is_featured=random.choice([True, False])
            )
            
            self.stdout.write(f'Created car: {car.title}')
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write('You can now browse cars in the admin panel.')
        self.stdout.write('Admin credentials: username: admin, password: admin123')