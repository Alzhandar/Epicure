from rest_framework import serializers
from .models import Menu, MenuType
from restaurant.models import Restaurant
from restaurant.serializers import RestaurantSerializer


class MenuTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuType
        fields = ['id', 'name']


class MenuSerializer(serializers.ModelSerializer):
    menu_type_details = MenuTypeSerializer(source='menu_type', read_only=True)
    restaurant_details = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = [
            'id', 'restaurant_details', 'menu_type_details',
            'name_ru', 'name_kz', 'image', 'image_url', 'description_ru', 'description_kz',
            'calories', 'proteins', 'fats', 'carbohydrates', 'price',
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_restaurant_details(self, obj):
        from restaurant.serializers import RestaurantMinSerializer
        return RestaurantMinSerializer(obj.restaurant).data if obj.restaurant else None
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class MenuMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name_ru', 'name_kz', 'price', 'is_available']