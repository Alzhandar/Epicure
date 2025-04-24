import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, F
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Banner
from .serializers import BannerSerializer

logger = logging.getLogger(__name__)

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Получить список активных баннеров",
        responses={200: BannerSerializer(many=True)}
    )
    def list(self, request):
        """Список всех активных баннеров"""
        now = timezone.now()
        banners = Banner.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            Q(end_date__gte=now) | Q(end_date__isnull=True)
        ).order_by('-priority', '-start_date')
        
        serializer = self.get_serializer(banners, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Получить информацию о баннере по ID",
        responses={
            200: BannerSerializer,
            404: "Баннер не найден"
        }
    )
    def retrieve(self, request, pk=None):
        """Получить детали баннера по ID"""
        banner = get_object_or_404(Banner, pk=pk)
        serializer = self.get_serializer(banner)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Зарегистрировать клик по баннеру",
        responses={
            200: openapi.Response("Успешный клик", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                    'clicks': openapi.Schema(type=openapi.TYPE_INTEGER, example=42)
                }
            )),
            404: "Баннер не найден"
        }
    )
    @action(detail=True, methods=['post'])
    def click(self, request, pk=None):
        """Зарегистрировать клик по баннеру и вернуть URL для перенаправления"""
        banner = get_object_or_404(Banner, pk=pk)
        banner.record_click()
        
        return Response({
            'status': 'success',
            'clicks': banner.clicks,
            'redirect_url': banner.url or '/'
        })
    
    @swagger_auto_schema(
        operation_description="Зарегистрировать показ баннера",
        responses={
            200: openapi.Response("Успешный показ", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='success'),
                    'impressions': openapi.Schema(type=openapi.TYPE_INTEGER, example=100)
                }
            )),
            404: "Баннер не найден"
        }
    )
    @action(detail=True, methods=['post'])
    def impression(self, request, pk=None):
        """Зарегистрировать показ баннера"""
        banner = get_object_or_404(Banner, pk=pk)
        banner.record_impression()
        
        return Response({
            'status': 'success',
            'impressions': banner.impressions
        })
    
    @swagger_auto_schema(
        operation_description="Получить активные баннеры по позиции",
        manual_parameters=[
            openapi.Parameter(
                'position', 
                openapi.IN_QUERY, 
                description="Позиция баннера (hero, above_restaurants, above_dishes)", 
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'limit', 
                openapi.IN_QUERY, 
                description="Максимальное количество баннеров", 
                type=openapi.TYPE_INTEGER,
                default=1
            ),
        ],
        responses={200: BannerSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_position(self, request):
        """Получить баннеры по позиции на странице"""
        position = request.query_params.get('position', 'hero')
        limit = int(request.query_params.get('limit', 1))
        
        banners = get_current_banners(position=position, limit=limit)
        serializer = self.get_serializer(banners, many=True)
        
        return Response(serializer.data)

def get_current_banners(position='hero', limit=1):
    now = timezone.now()
    banners = Banner.objects.filter(
        is_active=True,
        position=position,
        start_date__lte=now
    ).filter(
        Q(end_date__gte=now) | Q(end_date__isnull=True)
    ).order_by('-priority', '-start_date')[:limit]
    
    return banners

@require_GET
def banner_click(request, banner_id):
    try:
        banner = get_object_or_404(Banner, pk=banner_id)
        banner.record_click()
        
        if not banner.url:
            return redirect(request.META.get('HTTP_REFERER', '/'))
            
        return redirect(banner.url)
    except Exception as e:
        logger.error(f"Error processing banner click: {e}")
        return redirect('/')

@csrf_exempt
@require_POST
def banner_impression(request, banner_id):
    try:
        banner = get_object_or_404(Banner, pk=banner_id)
        banner.record_impression()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error recording banner impression: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_banners_for_homepage(request):
    context = {
        'hero_banners': get_current_banners(position='hero', limit=1),
        'restaurant_banners': get_current_banners(position='above_restaurants', limit=1),
        'dish_banners': get_current_banners(position='above_dishes', limit=1),
    }
    
    return context