import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'lagech.settings'
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

email = 'lagechtechnologies@gmail.com'
password = 'Lagech@2026'

u, created = User.objects.get_or_create(
    email=email,
    defaults={
        'username': email,
        'first_name': 'Lagech',
        'last_name': 'Admin',
    }
)
u.set_password(password)
u.save()

UserProfile.objects.get_or_create(user=u, defaults={'auth_provider': 'email'})

action = 'Created' if created else 'Updated'
print(f'{action} admin user: {email}')
print(f'Password: {password}')
