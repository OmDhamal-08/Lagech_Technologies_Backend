from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_view, name='auth-register'),
    path('login/', views.login_view, name='auth-login'),
    path('logout/', views.logout_view, name='auth-logout'),
    path('me/', views.me_view, name='auth-me'),
    path('google/', views.google_login_view, name='auth-google'),
    path('profile/', views.profile_view, name='auth-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
