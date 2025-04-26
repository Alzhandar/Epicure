from rest_framework import serializers
from .models import Restaurant, Table, Section
from cities.serializers import CitySerializer

class RestaurantSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'city', 'opening_time', 'closing_time', 'iiko_organization_id', 'external_menu_id', 'price_category_id', 'department_id', 'photo']

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

