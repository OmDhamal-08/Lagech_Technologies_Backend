from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'auth_provider', 'created_at']
    list_filter = ['auth_provider', 'city']
    search_fields = ['user__email', 'user__first_name', 'phone']
