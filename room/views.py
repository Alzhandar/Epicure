from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import models

from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action

from .models import Reservation, ReservationStatus
from .serializers import (
    ReservationSerializer, ReservationCreateSerializer,
    TimeSlotSerializer, TableAvailabilitySerializer
)
from restaurant.models import Restaurant, Table, Section
from restaurant.serializers import TableSerializer, SectionSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    filterset_fields = ['restaurant', 'table', 'reservation_date', 'status']
    search_fields = ['guest_name', 'guest_phone', 'guest_email']
    ordering_fields = ['reservation_date', 'start_time', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    @action(detail=False, methods=['GET'])
    def my_reservations(self, request):
        phone = request.query_params.get('phone')
        email = request.query_params.get('email')
        
        if not phone and not email:
            return Response(
                {"error": "Требуется указать телефон или email"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        queryset = self.get_queryset()
        if phone:
            queryset = queryset.filter(guest_phone=phone)
        if email:
            queryset = queryset.filter(guest_email=email)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TableAvailabilityView(APIView):
    def get(self, request):
        serializer = TableAvailabilitySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        restaurant_id = data['restaurant_id']
        date = data['date']
        guest_count = data.get('guest_count', 1)
        
        tables = Table.objects.filter(section__restaurant_id=restaurant_id)
        if guest_count:
            tables = tables.filter(capacity__gte=guest_count)
            
        booked_table_ids = Reservation.objects.filter(
            restaurant_id=restaurant_id,
            reservation_date=date,
            status__in=[ReservationStatus.CONFIRMED, ReservationStatus.PENDING]
        ).values_list('table_id', flat=True)
        
        available_tables = tables.exclude(id__in=booked_table_ids)
        
        result = {
            'restaurant_id': restaurant_id,
            'date': date,
            'available_tables': TableSerializer(available_tables, many=True).data
        }
        return Response(result)


class AvailableTimeSlotsView(APIView):
    def get(self, request):
        restaurant_id = request.query_params.get('restaurant')
        table_id = request.query_params.get('table')
        date_str = request.query_params.get('date')
        
        if not all([restaurant_id, table_id, date_str]):
            return Response(
                {"error": "Требуются параметры restaurant, table и date"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Неверный формат даты. Используйте YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        opening_time = datetime.strptime("10:00", "%H:%M").time()
        closing_time = datetime.strptime("22:00", "%H:%M").time()
        
        slots = []
        current_time = opening_time
        slot_duration = timedelta(hours=2)
        
        while current_time < closing_time:
            start_time = current_time
            end_time = (datetime.combine(date, start_time) + slot_duration).time()
            
            if end_time > closing_time:
                end_time = closing_time
                
            is_available = not Reservation.objects.filter(
                restaurant_id=restaurant_id,
                table_id=table_id,
                reservation_date=date,
                status__in=[ReservationStatus.CONFIRMED, ReservationStatus.PENDING]
            ).filter(
                models.Q(start_time__lt=end_time, end_time__gt=start_time)
            ).exists()
            
            slots.append({
                'start_time': start_time,
                'end_time': end_time,
                'available': is_available
            })
            
            current_time = (datetime.combine(date, start_time) + slot_duration).time()
            
        serializer = TimeSlotSerializer(slots, many=True)
        return Response(serializer.data)


class CheckReservationConflictView(APIView):
    def post(self, request):
        table_id = request.data.get('table')
        date = request.data.get('reservation_date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        if not all([table_id, date, start_time, end_time]):
            return Response(
                {"error": "Требуются параметры table, reservation_date, start_time и end_time"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        conflicts = Reservation.objects.filter(
            table_id=table_id,
            reservation_date=date,
            status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED]
        )
        
        has_conflict = conflicts.filter(
            models.Q(start_time__lt=end_time, end_time__gt=start_time)
        ).exists()
        
        return Response({"has_conflict": has_conflict})


class RestaurantTablesView(APIView):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        sections = Section.objects.filter(restaurant=restaurant)
        
        result = {
            'restaurant_id': restaurant_id,
            'restaurant_name': restaurant.name,
            'sections': []
        }
        
        for section in sections:
            tables = Table.objects.filter(section=section)
            section_data = {
                'id': section.id,
                'name': section.name,
                'tables': TableSerializer(tables, many=True).data
            }
            result['sections'].append(section_data)
            
        return Response(result)


class CancelReservationView(generics.UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation.status = ReservationStatus.CANCELLED
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)


class ConfirmReservationView(generics.UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation.status = ReservationStatus.CONFIRMED
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)


class CompleteReservationView(generics.UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation.status = ReservationStatus.COMPLETED
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)


class NoShowReservationView(generics.UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation.status = ReservationStatus.NO_SHOW
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)