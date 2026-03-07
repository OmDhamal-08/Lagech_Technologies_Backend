from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extends Django User with additional fields for Lagech.
    Created automatically on signup.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    auth_provider = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('google', 'Google')],
        default='email'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} ({self.auth_provider})"
