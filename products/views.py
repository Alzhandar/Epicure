import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Menu


logger = logging.getLogger(__name__)

def get_dish_details(request, dish_id):
    """
    API endpoint для получения детальной информации о блюде по ID.
    Возвращает детали блюда в формате JSON, включая информацию о
    ресторане, пищевой ценности и доступности.
    """
    try:
        # Получение блюда с предзагрузкой связанных объектов
        dish = get_object_or_404(Menu.objects.select_related('restaurant', 'menu_type'), id=dish_id)
        
        # Безопасное получение связанных данных
        restaurant_data = {'id': None, 'name': 'Не указан'}
        if dish.restaurant:
            restaurant_data = {
                'id': dish.restaurant.id,
                'name': dish.restaurant.name,
            }
            
        # Безопасное получение URL изображения
        image_url = None
        if dish.image:
            try:
                image_url = dish.image.url
            except Exception as e:
                logger.warning(f"Не удалось получить URL изображения для блюда {dish_id}: {e}")
        
        # Формирование ответа с безопасными проверками
        data = {
            'id': dish.id,
            'name': dish.name_ru,
            'description': dish.description_ru or 'Описание отсутствует',
            'price': str(dish.price) if hasattr(dish, 'price') else '0.00',
            'image': image_url,
            'menu_type': dish.menu_type.name if dish.menu_type else 'Основное меню',
            'restaurant': restaurant_data,
            'nutrition': {
                'calories': dish.calories or 'Н/Д',
                'proteins': str(dish.proteins) if dish.proteins else 'Н/Д',
                'fats': str(dish.fats) if dish.fats else 'Н/Д',
                'carbohydrates': str(dish.carbohydrates) if dish.carbohydrates else 'Н/Д',
            },
        }
        
        # Безопасный вызов методов
        try:
            data['is_healthy'] = dish.is_healthy()
        except Exception as e:
            logger.warning(f"Ошибка в методе is_healthy для блюда {dish_id}: {e}")
            data['is_healthy'] = False
            
        data['is_available'] = getattr(dish, 'is_available', True)
        
        return JsonResponse(data)
    except Exception as e:
        # Подробное логирование ошибки для отладки
        logger.error(f"Ошибка при получении данных о блюде {dish_id}: {e}", exc_info=True)
        # Клиенту возвращаем только общее сообщение об ошибке
        return JsonResponse({'error': 'Произошла ошибка при получении данных о блюде'}, status=500)