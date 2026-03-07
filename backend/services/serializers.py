from rest_framework import serializers
from .models import Category, ServiceRequest


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializes Category for the frontend.
    Output matches the shape expected by React CategoryCard/CategoryGrid.
    """
    priceRange = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'priceRange']

    def get_priceRange(self, obj):
        return {
            'min': float(obj.price_min),
            'max': float(obj.price_max),
        }


class ServiceRequestCreateSerializer(serializers.Serializer):
    """
    Validates incoming service request from frontend.
    Expects: { category_id: int, phone: str, name: str (optional) }
    """
    category_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')

    def validate_phone(self, value):
        # Strip spaces and ensure it starts with country code
        cleaned = value.strip().replace(' ', '').replace('-', '')
        if not cleaned.startswith('+'):
            cleaned = '+91' + cleaned  # Default to India
        if len(cleaned) < 10:
            raise serializers.ValidationError("Phone number is too short.")
        return cleaned

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive category.")
        return value


class ServiceRequestSerializer(serializers.ModelSerializer):
    """Full serializer for reading ServiceRequest details."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = ['id', 'category', 'category_name', 'customer_phone',
                  'customer_name', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
