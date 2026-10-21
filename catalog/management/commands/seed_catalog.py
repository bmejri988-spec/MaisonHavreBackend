from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import ChaletModel, Option, Terrain


MODELS = [
    ('horizon', 'Horizon', 'Light, openness, and uninterrupted views.', 'Contemporary', 120, 2, 2, 4, 280000, 'https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=1800&q=90'),
    ('atlas', 'Atlas', 'A warm retreat inspired by the mountains.', 'Mountain', 160, 3, 2, 6, 340000, 'https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?auto=format&fit=crop&w=1800&q=90'),
    ('terra', 'Terra', 'A grounded retreat shaped by nature.', 'Nature', 95, 2, 1, 4, 230000, 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1800&q=90'),
]

TERRAINS = [
    ('tabarka', 'Tabarka', 'Northwest Tunisia', 'coast', 'Tunisia', 450, 180000, 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=90'),
    ('ain-draham', 'Ain Draham', 'Northwest Tunisia', 'mountain', 'Tunisia', 600, 150000, 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=90'),
    ('cap-bon', 'Cap Bon', 'Northeast Tunisia', 'coast', 'Tunisia', 400, 200000, 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=1600&q=90'),
    ('zaghouan', 'Zaghouan', 'Northern Tunisia', 'mountain', 'Tunisia', 500, 160000, 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1600&q=90'),
]

OPTIONS = [
    ('infinity-pool', 'Infinity Pool', 'outdoor', 45000, True, 'Extend the horizon with a private pool designed around the landscape.', 'https://images.unsplash.com/photo-1572331165267-854da2b10ccc?auto=format&fit=crop&w=1400&q=90'),
    ('private-jacuzzi', 'Private Jacuzzi', 'outdoor', 18000, False, 'Create a private space for relaxation under the open sky.', 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=1400&q=90'),
    ('panoramic-terrace', 'Panoramic Terrace', 'outdoor', 22000, True, 'Turn the space around your chalet into an extension of your living area.', 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1400&q=90'),
    ('landscape-garden', 'Landscape Garden', 'outdoor', 15000, False, 'A carefully designed outdoor landscape that complements your chalet.', 'https://images.unsplash.com/photo-1558521958-0a228e77e984?auto=format&fit=crop&w=1400&q=90'),
    ('outdoor-fireplace', 'Outdoor Fireplace', 'outdoor', 12000, False, 'Bring warmth and atmosphere to evenings spent outside.', 'https://images.unsplash.com/photo-1478827536114-da961b7f86d2?auto=format&fit=crop&w=1400&q=90'),
    ('interior-fireplace', 'Interior Fireplace', 'interior', 14000, True, 'Create a warm focal point inside your chalet.', 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1400&q=90'),
    ('premium-kitchen', 'Premium Kitchen', 'interior', 28000, True, 'A refined kitchen designed for both everyday living and entertaining.', 'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1400&q=90'),
    ('interior-furniture-package', 'Interior Furniture Package', 'interior', 35000, False, 'A complete furniture selection designed around your chalet model.', 'https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?auto=format&fit=crop&w=1400&q=90'),
    ('smart-home', 'Smart Home', 'experience', 16000, False, 'Control lighting, climate and security from one intelligent system.', 'https://images.unsplash.com/photo-1558008258-3256797b43f3?auto=format&fit=crop&w=1400&q=90'),
    ('private-sauna', 'Private Sauna', 'experience', 24000, False, 'Turn your chalet into a complete private retreat.', 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1400&q=90'),
    ('architectural-lighting', 'Architectural Lighting', 'experience', 11000, False, 'Shape the atmosphere of your chalet after sunset.', 'https://images.unsplash.com/photo-1540932239986-30128078f3c5?auto=format&fit=crop&w=1400&q=90'),
    ('outdoor-kitchen', 'Outdoor Kitchen', 'outdoor', 20000, False, 'Bring cooking and entertaining outside.', 'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?auto=format&fit=crop&w=1400&q=90'),
]

MODEL_DETAILS = {
    'horizon': ('Horizon is designed around natural light and the relationship between interior and landscape. Large openings create a continuous dialogue between the chalet and its surroundings.', ['Panoramic windows', 'Open-plan living area', 'Private terrace', 'Natural materials']),
    'atlas': ('Atlas combines generous spaces with a strong architectural character. Designed for longer stays and family gatherings, it offers a deeper connection with its natural surroundings.', ['Three bedrooms', 'Large living space', 'Fireplace option', 'Mountain-facing terrace']),
    'terra': ('Terra is a more intimate chalet designed for those looking for simplicity, comfort and a strong connection with the landscape.', ['Compact footprint', 'Large outdoor area', 'Minimal architecture', 'Low-maintenance design']),
}

TERRAIN_DETAILS = {
    'tabarka': ('A unique setting where Mediterranean waters meet dense green landscapes, creating an exceptional environment for a private retreat.', ['Sea view', 'Natural surroundings', 'Easy road access']),
    'ain-draham': ('A peaceful mountain environment surrounded by forests and fresh air, ideal for a secluded countryside escape.', ['Forest surroundings', 'Mountain views', 'Quiet environment']),
    'cap-bon': ('A Mediterranean setting with open horizons, warm light and proximity to some of Tunisia’s most beautiful coastal landscapes.', ['Mediterranean views', 'Private environment', 'Close to the coast']),
    'zaghouan': ('A dramatic landscape combining mountain scenery and open countryside, offering a distinctive setting away from the city.', ['Mountain landscape', 'Open views', 'Natural surroundings']),
}


class Command(BaseCommand):
    help = 'Load the catalog seed data for local development.'

    @transaction.atomic
    def handle(self, *args, **options):
        for slug, name, subtitle, category, surface_area, bedrooms, bathrooms, max_guests, base_price, image in MODELS:
            description, features = MODEL_DETAILS[slug]
            ChaletModel.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'subtitle': subtitle, 'category': category, 'surface_area': surface_area, 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'max_guests': max_guests, 'base_price': base_price, 'description': description, 'image': image, 'gallery': [image], 'features': features},
            )

        for slug, name, region, _category, country, surface_area, base_price, image in TERRAINS:
            description, features = TERRAIN_DETAILS[slug]
            Terrain.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'region': region, 'country': country, 'surface_area': surface_area, 'base_price': base_price, 'description': description, 'image': image, 'gallery': [image], 'features': features},
            )

        for slug, name, _category, price, popular, short_description, image in OPTIONS:
            Option.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'short_description': short_description, 'description': short_description, 'price': price, 'image': image, 'popular': popular},
            )

        self.stdout.write(self.style.SUCCESS('Catalog seed data loaded.'))
