from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reservation_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient_email', 'recipient_phone', 'title', 
            'message', 'notification_type', 'notification_type_display',
            'status', 'status_display', 'reservation', 'reservation_details',
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