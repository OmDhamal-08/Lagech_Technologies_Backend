from django.contrib import admin
from .models import Category, ServiceRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'price_min', 'price_max', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_phone', 'customer_name', 'category', 'status',
                    'work_done', 'assigned_expert', 'created_at']
    list_filter = ['status', 'work_done', 'category', 'created_at']
    list_editable = ['status', 'work_done', 'assigned_expert']
    search_fields = ['customer_phone', 'customer_name', 'customer_email']
    readonly_fields = ['created_at', 'updated_at']
