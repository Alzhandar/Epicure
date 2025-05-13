from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone

from .models import Notification, NotificationStatus
from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Notification.objects.filter(
                user=self.request.user
            ).order_by('-created_at')
        return Notification.objects.none()
    
    @action(detail=False, methods=['GET'])
    def unread(self):
        queryset = self.get_queryset().filter(status=NotificationStatus.SENT)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        queryset = self.get_queryset().filter(
            status=NotificationStatus.SENT
        )
        
        updated_count = 0
        for notification in queryset:
            notification.mark_as_read()
            updated_count += 1
            
        return Response({
            "status": "success", 
            "message": f"Отмечено {updated_count} уведомлений как прочитанные",
            "updated_count": updated_count
        })


class GuestNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        email = self.request.query_params.get('email')
        phone = self.request.query_params.get('phone')
        
        if not email and not phone:
            return Notification.objects.none()
        
        queryset = Notification.objects.all()
        
        if email:
            queryset = queryset.filter(recipient_email=email)
        if phone:
            queryset = queryset.filter(recipient_phone=phone)
            
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        phone = request.query_params.get('phone')
        
        if not email and not phone:
            return Response(
                {"error": "Требуется указать email или телефон"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().list(request, *args, **kwargs)