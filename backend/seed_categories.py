"""
Seed default categories for Lagech.
Run: python manage.py shell < seed_categories.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lagech.settings')
django.setup()

from services.models import Category

CATEGORIES = [
    {"name": "Chimney", "slug": "chimney", "icon": "CookingPot", "description": "Deep cleaning, filter repair & installation", "price_min": 349, "price_max": 799, "order": 1},
    {"name": "Gas Stove", "slug": "gas-stove", "icon": "Flame", "description": "Burner repair, ignition fix & servicing", "price_min": 199, "price_max": 599, "order": 2},
    {"name": "Geyser", "slug": "geyser", "icon": "Thermometer", "description": "Heating element, thermostat & leak repair", "price_min": 299, "price_max": 899, "order": 3},
    {"name": "Washing Machine", "slug": "washing-machine", "icon": "WashingMachine", "description": "Drum repair, drain fix & servicing", "price_min": 299, "price_max": 899, "order": 4},
    {"name": "Plumbing", "slug": "plumbing", "icon": "Wrench", "description": "Pipe leaks, blockage & fitting repair", "price_min": 199, "price_max": 699, "order": 5},
    {"name": "AC / Cooler", "slug": "ac-cooler", "icon": "Wind", "description": "Gas refill, servicing & cooling issues", "price_min": 399, "price_max": 1499, "order": 6},
]

created_count = 0
for cat_data in CATEGORIES:
    obj, created = Category.objects.get_or_create(
        slug=cat_data["slug"],
        defaults=cat_data
    )
    if created:
        created_count += 1
        print(f"  Created: {obj.name}")
    else:
        print(f"  Already exists: {obj.name}")

print(f"\nDone! {created_count} new categories created.")
