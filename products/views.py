import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Menu, MenuType
from .serializers import MenuSerializer, MenuTypeSerializer

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dish_details(request, dish_id):
    try:
        dish = get_object_or_404(Menu.objects.select_related('restaurant', 'menu_type'), id=dish_id)

        # локализация
        lang = 'ru'
        if request.user.is_authenticated:
            lang = getattr(request.user, 'language', 'ru') or 'ru'

        name = dish.name_kz if lang == 'kz' and dish.name_kz else dish.name_ru
        description = dish.description_kz if lang == 'kz' and dish.description_kz else dish.description_ru or 'Описание отсутствует'
        menu_type_name = dish.menu_type.name_kz if lang == 'kz' and dish.menu_type and dish.menu_type.name_kz else dish.menu_type.name if dish.menu_type else 'Основное меню'

        restaurant_data = {'id': None, 'name': 'Не указан'}
        if dish.restaurant:
            restaurant_data = {
                'id': dish.restaurant.id,
                'name': dish.restaurant.name,
            }

        image_url = None
        if dish.image:
            try:
                image_url = dish.image.url
            except Exception as e:
                logger.warning(f"Не удалось получить URL изображения для блюда {dish_id}: {e}")

        data = {
            'id': dish.id,
            'name': name,
            'description': description,
            'price': str(dish.price) if hasattr(dish, 'price') else '0.00',
            'image': image_url,
            'menu_type': menu_type_name,
            'restaurant': restaurant_data,
            'nutrition': {
                'calories': dish.calories or 'Н/Д',
                'proteins': str(dish.proteins) if dish.proteins else 'Н/Д',
                'fats': str(dish.fats) if dish.fats else 'Н/Д',
                'carbohydrates': str(dish.carbohydrates) if dish.carbohydrates else 'Н/Д',
            },
        }

        try:
            data['is_healthy'] = dish.is_healthy()
        except Exception as e:
            logger.warning(f"Ошибка в методе is_healthy для блюда {dish_id}: {e}")
            data['is_healthy'] = False

        data['is_available'] = getattr(dish, 'is_available', True)

        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Ошибка при получении данных о блюде {dish_id}: {e}", exc_info=True)
        return JsonResponse({'error': 'Произошла ошибка при получении данных о блюде'}, status=500)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filterset_fields = ['restaurant', 'menu_type', 'is_available']
    search_fields = ['name_ru', 'name_kz', 'description_ru', 'description_kz']
    ordering_fields = ['price', 'calories', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        menu_type = self.request.query_params.get('menu_type')
        if menu_type:
            queryset = queryset.filter(menu_type_id=menu_type)

        return queryset

    @action(detail=False, methods=['GET'])
    def available(self, request):
        queryset = self.get_queryset().filter(is_available=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def toggle_availability(self, request, pk=None):
        menu_item = self.get_object()
        menu_item.is_available = not menu_item.is_available
        menu_item.save()
        serializer = self.get_serializer(menu_item)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def popular(self, request):
        queryset = self.get_queryset().filter(is_popular=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def toggle_popularity(self, request, pk=None):
        menu_item = self.get_object()
        menu_item.is_popular = not menu_item.is_popular
        menu_item.save()
        serializer = self.get_serializer(menu_item)
        return Response(serializer.data)


class MenuTypeViewSet(viewsets.ModelViewSet):
    queryset = MenuType.objects.all()
    serializer_class = MenuTypeSerializer
