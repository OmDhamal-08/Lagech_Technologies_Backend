"""
Auth API views: Register, Login, Logout, Me, GoogleLogin, Profile.
"""
import logging
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer, LoginSerializer, GoogleAuthSerializer,
    UserSerializer, UserProfileUpdateSerializer,
)
from .models import UserProfile

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    """Generate JWT access + refresh tokens."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    POST /api/auth/register/
    Body: { first_name, last_name, email, password }
    """
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    user = serializer.save()
    tokens = get_tokens_for_user(user)
    user_data = UserSerializer(user).data

    logger.info(f"[Auth] New user registered: {user.email}")
    return Response({
        'success': True,
        'user': user_data,
        'tokens': tokens,
    }, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/auth/login/
    Body: { email, password }
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    user = serializer.validated_data['user']
    tokens = get_tokens_for_user(user)
    user_data = UserSerializer(user).data

    logger.info(f"[Auth] User logged in: {user.email}")
    return Response({
        'success': True,
        'user': user_data,
        'tokens': tokens,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/auth/logout/
    Body: { refresh }  — blacklist the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass  # Token may already be blacklisted
    return Response({'success': True, 'message': 'Logged out.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/auth/me/
    Returns the current user's profile.
    """
    user_data = UserSerializer(request.user).data
    return Response({'success': True, 'user': user_data})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET  /api/auth/profile/ — returns full profile with bookings info.
    PATCH /api/auth/profile/ — updates phone, city, address.
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(
        user=user, defaults={'auth_provider': 'email'}
    )

    if request.method == 'PATCH':
        serializer = UserProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=400)

        data = serializer.validated_data
        if 'phone' in data:
            profile.phone = data['phone']
        if 'city' in data:
            profile.city = data['city']
        if 'address' in data:
            profile.address = data['address']
        profile.save()

        logger.info(f"[Auth] Profile updated for: {user.email}")

    # Build response with full profile + recent bookings
    user_data = UserSerializer(user).data

    # Fetch recent bookings
    from services.models import ServiceRequest
    recent_bookings = ServiceRequest.objects.filter(user=user).order_by('-created_at')[:10]
    bookings_data = [
        {
            'id': b.id,
            'category_name': b.category.name,
            'status': b.status,
            'status_display': b.get_status_display(),
            'customer_phone': b.customer_phone,
            'created_at': b.created_at.strftime('%d %b %Y, %I:%M %p'),
        }
        for b in recent_bookings
    ]

    return Response({
        'success': True,
        'user': user_data,
        'recent_bookings': bookings_data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_view(request):
    """
    POST /api/auth/google/
    Body: { token }  — Google OAuth access token from frontend.

    Verifies with Google, creates/finds user, returns JWT tokens.
    """
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    google_token = serializer.validated_data['token']

    # Verify token with Google
    try:
        import requests as http_requests
        google_resp = http_requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {google_token}'},
            timeout=10,
        )
        if google_resp.status_code != 200:
            return Response({'success': False, 'error': 'Invalid Google token'}, status=400)

        google_data = google_resp.json()
        email = google_data.get('email', '').lower()
        first_name = google_data.get('given_name', '')
        last_name = google_data.get('family_name', '')

        if not email:
            return Response({'success': False, 'error': 'No email from Google'}, status=400)

    except Exception as e:
        logger.error(f"[Auth] Google verification failed: {e}")
        return Response({'success': False, 'error': 'Google verification failed'}, status=500)

    # Find or create user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    if created:
        user.set_unusable_password()  # Google users don't have passwords
        user.save()
        UserProfile.objects.create(user=user, auth_provider='google')
        logger.info(f"[Auth] New Google user created: {email}")
    else:
        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user, defaults={'auth_provider': 'google'})
        logger.info(f"[Auth] Google user logged in: {email}")

    tokens = get_tokens_for_user(user)
    user_data = UserSerializer(user).data

    return Response({
        'success': True,
        'user': user_data,
        'tokens': tokens,
        'is_new_user': created,
    })
