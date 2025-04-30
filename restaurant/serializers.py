from rest_framework import serializers
from .models import Restaurant, Table, Section, Review
from cities.serializers import CitySerializer
from users.serializers import UserSerializer


class RestaurantSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'city', 'opening_time', 'closing_time', 
            'description_ru', 'description_kz', 'rating', 'reviews_count',
            'iiko_organization_id', 'external_menu_id', 'price_category_id', 
            'department_id', 'photo'
        ]

class SectionSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()

    class Meta:
        model = Section
        fields = ['id', 'name', 'restaurant', 'photo']

class TableSerializer(serializers.ModelSerializer):
    section = SectionSerializer()

    class Meta:
        model = Table
        fields = ['uuid', 'number', 'section', 'qr', 'call_waiter', 'call_time', 'bill_waiter', 'bill_time', 'iiko_waiter_id']

class RestaurantMinSerializer(serializers.ModelSerializer):
    city_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'city', 'city_name']
    
    def get_city_name(self, obj):
        return obj.city.name if obj.city else None

class ReviewSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'restaurant', 'restaurant_name', 'user', 'user_details',
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, attrs):
        user = attrs.get('user') or self.context['request'].user
        restaurant = attrs.get('restaurant')
        
        instance = getattr(self, 'instance', None)
        if instance and instance.restaurant.id != restaurant.id:
            raise serializers.ValidationError(
                {"restaurant": "Нельзя изменить ресторан в существующем отзыве"}
            )
            
        if not instance and Review.objects.filter(user=user, restaurant=restaurant).exists():
            raise serializers.ValidationError(
                {"non_field_errors": "Вы уже оставили отзыв для этого ресторана"}
            )
            
        return attrs