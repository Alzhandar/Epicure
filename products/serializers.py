from rest_framework import serializers
from .models import Menu, MenuType
from restaurant.models import Restaurant
from restaurant.serializers import RestaurantSerializer


class MenuTypeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = MenuType
        fields = ['id', 'name']

    def get_name(self, obj):
        request = self.context.get('request')
        lang = 'ru'
        if request and request.user.is_authenticated:
            lang = getattr(request.user, 'language', 'ru') or 'ru'
        return obj.name_kz if lang == 'kz' and obj.name_kz else obj.name


class MenuSerializer(serializers.ModelSerializer):
    menu_type_details = MenuTypeSerializer(source='menu_type', read_only=True)
    restaurant_details = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id', 'restaurant_details', 'menu_type_details',
            'name', 'name_ru', 'name_kz',
            'image', 'image_url',
            'description', 'description_ru', 'description_kz',
            'calories', 'proteins', 'fats', 'carbohydrates', 'price',
            'is_available', 'is_popular', 'created_at', 'updated_at'
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

    def get_name(self, obj):
        request = self.context.get('request')
        lang = 'ru'
        if request and request.user.is_authenticated:
            lang = getattr(request.user, 'language', 'ru') or 'ru'
        return obj.name_kz if lang == 'kz' and obj.name_kz else obj.name_ru

    def get_description(self, obj):
        request = self.context.get('request')
        lang = 'ru'
        if request and request.user.is_authenticated:
            lang = getattr(request.user, 'language', 'ru') or 'ru'
        return obj.description_kz if lang == 'kz' and obj.description_kz else obj.description_ru



class MenuMinSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'price', 'is_available']

    def get_name(self, obj):
        request = self.context.get('request')
        lang = 'ru'
        if request and request.user.is_authenticated:
            lang = getattr(request.user, 'language', 'ru') or 'ru'
        return obj.name_kz if lang == 'kz' and obj.name_kz else obj.name_ru
