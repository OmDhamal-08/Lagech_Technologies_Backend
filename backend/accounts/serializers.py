from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile


class RegisterSerializer(serializers.Serializer):
    """Register with email + password."""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
        )
        UserProfile.objects.create(user=user, auth_provider='email')
        return user


class LoginSerializer(serializers.Serializer):
    """Login with email + password."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'].lower(), password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data['user'] = user
        return data


class GoogleAuthSerializer(serializers.Serializer):
    """Google OAuth — receives the Google access token from frontend."""
    token = serializers.CharField()


class UserProfileUpdateSerializer(serializers.Serializer):
    """Validates profile update fields (phone, city, address)."""
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        cleaned = value.strip().replace(' ', '').replace('-', '')
        if cleaned and len(cleaned) < 10:
            raise serializers.ValidationError("Phone number is too short.")
        if cleaned and not cleaned.startswith('+'):
            cleaned = '+91' + cleaned
        return cleaned


class UserSerializer(serializers.ModelSerializer):
    """Serialize user data for the frontend."""
    phone = serializers.CharField(source='profile.phone', read_only=True)
    city = serializers.CharField(source='profile.city', read_only=True)
    address = serializers.CharField(source='profile.address', read_only=True)
    auth_provider = serializers.CharField(source='profile.auth_provider', read_only=True)
    total_bookings = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city',
                  'address', 'auth_provider', 'total_bookings', 'member_since']

    def get_total_bookings(self, obj):
        return obj.service_requests.count()

    def get_member_since(self, obj):
        return obj.date_joined.strftime('%b %Y')
