from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
import uuid

from .models import Offer, OfferItem, OfferReservation
from .serializers import (
    OfferSerializer, 
    OfferDetailSerializer, 
    OfferCreateSerializer, 
    OfferItemSerializer,
    OfferReservationSerializer
)
from restaurant.models import Table, Restaurant
from cities.models import City


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['restaurant', 'offer_type', 'people_count']
    search_fields = ['title_ru', 'title_kz']
    ordering_fields = ['new_price', 'created_at', 'people_count']
    ordering = ['new_price']
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return OfferCreateSerializer
        elif self.action == 'retrieve':
            return OfferDetailSerializer
        return OfferSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        city_id = self.request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(restaurant__city_id=city_id)
            
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(new_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(new_price__lte=max_price)
            
        return queryset
    
    @swagger_auto_schema(
        operation_description="Получить список предложений по городу",
        manual_parameters=[
            openapi.Parameter(
                'city_id', 
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='ID города'
            ),
        ],
        responses={
            200: OfferSerializer(many=True)
        },
        tags=['offers']
    )
    @action(detail=False, methods=['get'])
    def by_city(self, request):
        city_id = request.query_params.get('city_id')
        if not city_id:
            return Response(
                {"error": "Необходимо указать ID города (city_id)"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response(
                {"error": "Город с указанным ID не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        offers = self.get_queryset().filter(restaurant__city=city)
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Получить доступные столы для предложения на указанную дату и время",
        manual_parameters=[
            openapi.Parameter(
                'date', 
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                description='Дата в формате YYYY-MM-DD'
            ),
            openapi.Parameter(
                'time', 
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                description='Время в формате HH:MM'
            ),
        ],
        responses={
            200: openapi.Response(
                description="Список доступных столов",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING),
                            'number': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'section': openapi.Schema(type=openapi.TYPE_OBJECT)
                        }
                    )
                )
            ),
            400: "Некорректные параметры запроса",
            404: "Предложение не найдено"
        },
        tags=['offers']
    )
    @action(detail=True, methods=['get'])
    def available_tables(self, request, pk=None):
        offer = self.get_object()
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')
        
        if not date_str or not time_str:
            return Response(
                {"error": "Необходимо указать дату (date) и время (time)"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return Response(
                {"error": "Некорректный формат даты или времени. Используйте YYYY-MM-DD для даты и HH:MM для времени"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booked_tables = OfferReservation.objects.filter(
            date=date,
            time__range=(
                (time.replace(hour=time.hour-1) if time.hour > 0 else time),
                (time.replace(hour=time.hour+1) if time.hour < 23 else time)
            ),
            status__in=['pending', 'confirmed']
        ).values_list('table_id', flat=True)
        
        available_tables = Table.objects.filter(
            section__restaurant=offer.restaurant
        ).exclude(
            uuid__in=booked_tables
        )
        
        from restaurant.serializers import TableSerializer
        serializer = TableSerializer(available_tables, many=True)
        return Response(serializer.data)


class OfferItemViewSet(viewsets.ModelViewSet):
    queryset = OfferItem.objects.all()
    serializer_class = OfferItemSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['offer']


class OfferReservationViewSet(viewsets.ModelViewSet):
    serializer_class = OfferReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['offer', 'date', 'status']
    ordering_fields = ['date', 'time', 'created_at']
    ordering = ['-date', '-time']
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return OfferReservation.objects.all()
        return OfferReservation.objects.filter(user=user)
    
    @swagger_auto_schema(
        operation_description="Отменить бронирование",
        responses={
            200: "Бронирование успешно отменено",
            400: "Ошибка при отмене бронирования",
            404: "Бронирование не найдено"
        },
        tags=['offer-reservations']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "У вас нет прав для отмены этого бронирования"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if reservation.status == 'cancelled':
            return Response(
                {"error": "Бронирование уже отменено"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if reservation.date < timezone.now().date():
            return Response(
                {"error": "Невозможно отменить бронирование на прошедшую дату"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        reservation.status = 'cancelled'
        reservation.save()
        
        return Response({
            "status": "success",
            "message": "Бронирование успешно отменено"
        })
    
    @swagger_auto_schema(
        operation_description="Подтвердить бронирование (только для администраторов)",
        responses={
            200: "Бронирование успешно подтверждено",
            400: "Ошибка при подтверждении бронирования",
            404: "Бронирование не найдено"
        },
        tags=['offer-reservations']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def confirm(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.status != 'pending':
            return Response(
                {"error": f"Невозможно подтвердить бронирование в статусе '{reservation.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if reservation.date < timezone.now().date():
            return Response(
                {"error": "Невозможно подтвердить бронирование на прошедшую дату"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        reservation.status = 'confirmed'
        reservation.save()
        
        return Response({
            "status": "success",
            "message": "Бронирование успешно подтверждено"
        })
    
    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        reservations = OfferReservation.objects.filter(user=request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)