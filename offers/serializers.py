from rest_framework import serializers
from django.utils import timezone
from .models import Offer, OfferItem, OfferReservation
from restaurant.serializers import RestaurantMinSerializer, TableSerializer


class OfferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferItem
        fields = ['id', 'description_ru', 'description_kz', 'order']


class OfferSerializer(serializers.ModelSerializer):
    restaurant_details = RestaurantMinSerializer(source='restaurant', read_only=True)
    items = OfferItemSerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'restaurant', 'restaurant_details', 'title_ru', 'title_kz', 
            'image', 'image_url', 'old_price', 'new_price', 'badge', 
            'people_count', 'per_person', 'offer_type', 'items',
            'discount_percentage', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_discount_percentage(self, obj):
        if obj.old_price and obj.old_price > obj.new_price:
            discount = ((obj.old_price - obj.new_price) / obj.old_price) * 100
            return round(discount)
        return 0
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class OfferDetailSerializer(serializers.ModelSerializer):
    restaurant_details = RestaurantMinSerializer(source='restaurant', read_only=True)
    items = OfferItemSerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'restaurant', 'restaurant_details', 'title_ru', 'title_kz', 
            'image', 'image_url', 'old_price', 'new_price', 'badge', 
            'people_count', 'per_person', 'offer_type', 'items',
            'discount_percentage', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_discount_percentage(self, obj):
        if obj.old_price and obj.old_price > obj.new_price:
            discount = ((obj.old_price - obj.new_price) / obj.old_price) * 100
            return round(discount)
        return 0
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class OfferCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Offer
        fields = [
            'restaurant', 'title_ru', 'title_kz', 'image', 
            'old_price', 'new_price', 'badge', 'people_count', 
            'per_person', 'offer_type', 'is_active', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        offer = Offer.objects.create(**validated_data)
        
        for i, item_text in enumerate(items_data):
            OfferItem.objects.create(
                offer=offer,
                description_ru=item_text,
                order=i
            )
        
        return offer


class OfferReservationSerializer(serializers.ModelSerializer):
    offer_details = OfferSerializer(source='offer', read_only=True)
    table_details = TableSerializer(source='table', read_only=True)
    
    class Meta:
        model = OfferReservation
        fields = [
            'id', 'offer', 'offer_details', 'user', 'table', 'table_details',
            'date', 'time', 'guest_count', 'special_requests', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user', 'status']
    
    def validate(self, attrs):
        table = attrs.get('table')
        date = attrs.get('date')
        time = attrs.get('time')
        offer = attrs.get('offer')
        
        if date < timezone.now().date():
            raise serializers.ValidationError(
                {"date": "Невозможно забронировать на прошедшую дату"}
            )
        
        if table and table.section.restaurant != offer.restaurant:
            raise serializers.ValidationError(
                {"table": "Выбранный стол не принадлежит ресторану данного предложения"}
            )
            
        if table and OfferReservation.objects.filter(
            table=table,
            date=date,
            time__range=(
                (time.replace(hour=time.hour-1) if time.hour > 0 else time),
                (time.replace(hour=time.hour+1) if time.hour < 23 else time)
            ),
            status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError(
                {"table": "Выбранный стол уже забронирован на это время"}
            )
        
        if attrs.get('guest_count', 1) > offer.people_count:
            raise serializers.ValidationError({
                "guest_count": f"Это предложение рассчитано максимум на {offer.people_count} гостей"
            })
            
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)