from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # GET  /api/categories/          → list all active categories
    path('categories/', views.category_list, name='category-list'),
    
    # POST /api/request/             → create service request + send WhatsApp
    path('request/', views.create_service_request, name='create-request'),
    
    # GET  /api/my-bookings/         → authenticated user's booking history
    path('my-bookings/', views.my_bookings_view, name='my-bookings'),
    
    # POST /api/whatsapp/webhook/    → receive incoming WhatsApp replies (Twilio)
    path('whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp-webhook'),

    # ─── Admin endpoints (restricted to ADMIN_EMAIL) ─────────────
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin-dashboard'),
    path('admin/orders/', admin_views.admin_orders, name='admin-orders'),
    path('admin/orders/export/', admin_views.admin_export_excel, name='admin-export'),
    
    # ─── Temp DB Init Endpoint ─────────────
    path('init-db/', admin_views.init_db, name='init-db'),
]
