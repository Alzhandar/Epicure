from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Reservation, ReservationMenuItem, ReservationStatus
from restaurant.models import Restaurant, Table
from restaurant.serializers import RestaurantSerializer, TableSerializer
from products.models import Menu
from products.serializers import MenuSerializer


class ReservationMenuItemSerializer(serializers.ModelSerializer):
    menu_item_details = MenuSerializer(source='menu_item', read_only=True)
    
    class Meta:
        model = ReservationMenuItem
        fields = ['id', 'menu_item', 'menu_item_details', 'quantity']


class ReservationSerializer(serializers.ModelSerializer):
    menu_items = ReservationMenuItemSerializer(many=True, read_only=True)
    restaurant_details = RestaurantSerializer(source='restaurant', read_only=True)
    table_details = TableSerializer(source='table', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'restaurant', 'restaurant_details', 'table', 'table_details',
            'reservation_date', 'start_time', 'end_time', 'guest_count',
            'guest_name', 'guest_phone', 'guest_email', 'status', 'status_display',
            'special_requests', 'created_at', 'updated_at', 'menu_items'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, attrs):
        if attrs.get('reservation_date') and attrs['reservation_date'] < timezone.now().date():
            raise serializers.ValidationError({"reservation_date": "Нельзя создать бронирование на прошедшую дату"})
        
        if attrs.get('start_time') and attrs.get('end_time') and attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError({"end_time": "Время окончания должно быть позже времени начала"})
        
        if attrs.get('table') and attrs.get('restaurant'):
            if attrs['table'].section and attrs['table'].section.restaurant != attrs['restaurant']:
                raise serializers.ValidationError({
                    "table": "Выбранный стол не принадлежит указанному ресторану"
                })
        
        self._validate_booking_conflicts(attrs)
        
        return attrs
    
    def _validate_booking_conflicts(self, attrs):
        if not (attrs.get('table') and attrs.get('reservation_date') and 
                attrs.get('start_time') and attrs.get('end_time')):
            return
        
        instance_id = self.instance.id if self.instance else None
        
        conflicting_reservations = Reservation.objects.filter(
            table=attrs['table'],
            reservation_date=attrs['reservation_date'],
            status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED]
        )
        
        if instance_id:
            conflicting_reservations = conflicting_reservations.exclude(id=instance_id)
        
        for reservation in conflicting_reservations:
            if ((attrs['start_time'] <= reservation.start_time < attrs['end_time']) or
                (attrs['start_time'] < reservation.end_time <= attrs['end_time']) or
                (reservation.start_time <= attrs['start_time'] < reservation.end_time) or
                (attrs['start_time'] <= reservation.start_time and attrs['end_time'] >= reservation.end_time)):
                raise serializers.ValidationError({
                    "non_field_errors": [
                        f"Конфликт бронирования: стол уже забронирован с {reservation.start_time} до {reservation.end_time}"
                    ]
                })


class ReservationCreateSerializer(ReservationSerializer):
    menu_items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )
    
    def create(self, validated_data):
        menu_items_data = validated_data.pop('menu_items', [])
        reservation = Reservation.objects.create(**validated_data)
        
        for item_data in menu_items_data:
            menu_item_id = item_data.get('menu_item')
            quantity = item_data.get('quantity', 1)
            
            try:
                menu_item = Menu.objects.get(id=menu_item_id)
                ReservationMenuItem.objects.create(
                    reservation=reservation,
                    menu_item=menu_item,
                    quantity=quantity
                )
            except Menu.DoesNotExist:
                pass 
        
        return reservation


class TimeSlotSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    available = serializers.BooleanField()


class TableAvailabilitySerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    date = serializers.DateField()
    guest_count = serializers.IntegerField(required=False, min_value=1)