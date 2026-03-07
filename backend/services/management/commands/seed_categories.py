"""
Management command to seed initial categories.
Run: python manage.py seed_categories
"""

from django.core.management.base import BaseCommand
from services.models import Category


INITIAL_CATEGORIES = [
    {
        'name': 'Chimney',
        'slug': 'chimney',
        'icon': 'CookingPot',
        'description': 'Deep cleaning, filter repair & installation',
        'price_min': 349,
        'price_max': 799,
        'order': 1,
    },
    {
        'name': 'Gas Stove',
        'slug': 'gas-stove',
        'icon': 'Flame',
        'description': 'Burner repair, ignition fix & servicing',
        'price_min': 199,
        'price_max': 599,
        'order': 2,
    },
    {
        'name': 'Geyser',
        'slug': 'geyser',
        'icon': 'Thermometer',
        'description': 'Heating element, thermostat & leak repair',
        'price_min': 299,
        'price_max': 899,
        'order': 3,
    },
    {
        'name': 'Electrical',
        'slug': 'electrical',
        'icon': 'Zap',
        'description': 'Wiring, switches, MCB & short circuit',
        'price_min': 149,
        'price_max': 699,
        'order': 4,
    },
    {
        'name': 'Bathroom',
        'slug': 'bathroom',
        'icon': 'ShowerHead',
        'description': 'Tap, shower, flush & tile repair',
        'price_min': 199,
        'price_max': 799,
        'order': 5,
    },
    {
        'name': 'Plumbing',
        'slug': 'plumbing',
        'icon': 'Wrench',
        'description': 'Pipe leaks, blockage & fitting repair',
        'price_min': 199,
        'price_max': 699,
        'order': 6,
    },
    {
        'name': 'AC / Cooler',
        'slug': 'ac-cooler',
        'icon': 'Wind',
        'description': 'Gas refill, servicing & cooling issues',
        'price_min': 399,
        'price_max': 1499,
        'order': 7,
    },
    {
        'name': 'Other',
        'slug': 'other',
        'icon': 'HelpCircle',
        'description': 'Carpentry, painting & general repairs',
        'price_min': 199,
        'price_max': 999,
        'order': 8,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with initial service categories'

    def handle(self, *args, **options):
        created_count = 0
        for cat_data in INITIAL_CATEGORIES:
            _, created = Category.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data,
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created: {cat_data['name']}")
            else:
                self.stdout.write(f"  ↻ Updated: {cat_data['name']}")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {created_count} new categories created, '
            f'{len(INITIAL_CATEGORIES) - created_count} updated.'
        ))
