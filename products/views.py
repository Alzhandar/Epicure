from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Menu

def get_dish_details(request, dish_id):
    try:
        dish = get_object_or_404(Menu.objects.select_related('restaurant', 'menu_type'), id=dish_id)
        data = {
            'id': dish.id,
            'name': dish.name_ru,
            'description': dish.description or 'Описание отсутствует',
            'price': str(dish.price),
            'image': dish.image.url if dish.image else None,
            'menu_type': dish.menu_type.name if dish.menu_type else 'Основное меню',
            'restaurant': {
                'id': dish.restaurant.id,
                'name': dish.restaurant.name,
            },
            'nutrition': {
                'calories': dish.calories or 'Н/Д',
                'proteins': str(dish.proteins) if dish.proteins else 'Н/Д',
                'fats': str(dish.fats) if dish.fats else 'Н/Д',
                'carbohydrates': str(dish.carbohydrates) if dish.carbohydrates else 'Н/Д',
            },
            'is_healthy': dish.is_healthy(),
            'is_available': dish.is_available,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)