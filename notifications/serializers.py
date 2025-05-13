from rest_framework import serializers
from django.utils import timezone

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reservation_details = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient_email', 'recipient_phone', 'title', 
            'message', 'notification_type', 'notification_type_display',
            'status', 'status_display', 'is_read', 'time_since',
            'reservation', 'reservation_details',
            'created_at', 'updated_at', 'read_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'read_at']
    
    def get_reservation_details(self, obj):
        if obj.reservation:
            return {
                'id': obj.reservation.id,
                'restaurant_name': obj.reservation.restaurant.name,
                'reservation_date': obj.reservation.reservation_date,
                'start_time': obj.reservation.start_time,
                'end_time': obj.reservation.end_time,
                'guest_count': obj.reservation.guest_count,
                'status': obj.reservation.status
            }
        return None
    
    def get_is_read(self, obj):
        return obj.status == 'read'
    
    def get_time_since(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 30:
            months = diff.days // 30
            return f"{months} {'месяц' if months == 1 else 'месяцев' if months >= 5 else 'месяца'} назад"
        elif diff.days > 0:
            return f"{diff.days} {'день' if diff.days == 1 else 'дня' if 2 <= diff.days <= 4 else 'дней'} назад"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} {'час' if hours == 1 else 'часа' if 2 <= hours <= 4 else 'часов'} назад"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} {'минуту' if minutes == 1 else 'минуты' if 2 <= minutes <= 4 else 'минут'} назад"
        else:
            return "только что"


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'recipient_email', 'recipient_phone', 'title', 'message', 
            'notification_type', 'reservation', 'user'
        ]
    
    def validate(self, data):
        if not data.get('recipient_email') and not data.get('user') and not data.get('recipient_phone'):
            raise serializers.ValidationError("Необходимо указать получателя: email, телефон или пользователя")
        
        if not data.get('user') and data.get('recipient_email'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=data.get('recipient_email'))
                data['user'] = user
            except User.DoesNotExist:
                pass
        
        return data