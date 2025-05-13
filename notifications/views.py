from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .models import Notification, NotificationStatus
from .serializers import NotificationSerializer
from .services import NotificationService

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Notification.objects.filter(
                Q(user=user) | Q(recipient_email=user.email)
            ).select_related('reservation').order_by('-created_at')
        return Notification.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('Непрочитанные уведомления', NotificationSerializer(many=True)),
            401: 'Unauthorized'
        }
    )
    @action(detail=False, methods=['GET'])
    def unread(self, request):
        queryset = self.get_queryset().filter(status=NotificationStatus.SENT)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('Уведомление отмечено как прочитанное', NotificationSerializer),
            404: 'Not Found',
            401: 'Unauthorized'
        }
    )
    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        
        user = request.user
        if (notification.user and notification.user != user) and notification.recipient_email != user.email:
            return Response(
                {"error": "Вы не имеете прав на изменение этого уведомления"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        logger.info(f"Уведомление {notification.id} отмечено как прочитанное пользователем {user.id}")
        return Response(serializer.data)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('Все уведомления отмечены как прочитанные', 
                                 openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                                        'updated_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    }
                                 )),
            401: 'Unauthorized'
        }
    )
    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        user = request.user
        queryset = self.get_queryset().filter(
            Q(status=NotificationStatus.SENT),
            Q(user=user) | Q(recipient_email=user.email)
        )
        
        now = timezone.now()
        updated_count = queryset.update(status=NotificationStatus.READ, read_at=now)
        
        logger.info(f"Пользователь {user.id} отметил все уведомления как прочитанные ({updated_count} уведомлений)")
        
        return Response({
            "status": "success", 
            "message": f"Отмечено {updated_count} уведомлений как прочитанные",
            "updated_count": updated_count
        })


class GuestNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_QUERY, description="Email гостя", type=openapi.TYPE_STRING),
            openapi.Parameter('phone', openapi.IN_QUERY, description="Телефон гостя", type=openapi.TYPE_STRING),
        ],
        responses={
            200: NotificationSerializer(many=True),
            400: "Необходимо указать email или телефон",
        }
    )
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
        
        logger.info(f"Запрос уведомлений для гостя с email={email}, phone={phone}, IP={request.META.get('REMOTE_ADDR')}")
        
        return super().list(request, *args, **kwargs)