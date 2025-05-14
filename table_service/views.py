from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce, Concat
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from restaurant.models import Table, Restaurant, Review
from products.models import Menu, MenuType
from .models import Order, OrderItem

import json
import uuid
import logging

logger = logging.getLogger(__name__)

def get_table_from_uuid(table_uuid):
    """Вспомогательная функция для получения стола по UUID"""
    try:
        table = Table.objects.select_related('section__restaurant').get(uuid=table_uuid)
        return table
    except Table.DoesNotExist:
        return None

def table_service_view(request, table_uuid):
    """Основная страница сервиса обслуживания стола"""
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.section.restaurant
    
    # Получаем или создаем активный заказ для стола
    active_order = Order.objects.filter(
        table=table, 
        status__in=['new', 'processing', 'ready', 'delivered']
    ).first()
    
    context = {
        'table': table,
        'restaurant': restaurant,
        'has_active_order': active_order is not None,
        'waiter_called': table.call_waiter,
        'bill_requested': table.bill_waiter
    }
    
    return render(request, 'table_service/index.html', context)

def menu_view(request, table_uuid):
    """Страница с меню ресторана"""
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.section.restaurant
    
    # Используем name_ru как основное имя для каждого типа меню
    menu_types = MenuType.objects.filter(menus__restaurant=restaurant).distinct().values('id', 'name_ru')
    
    active_order = Order.objects.filter(
        table=table, 
        status__in=['new', 'processing', 'ready', 'delivered']
    ).first()
    
    context = {
        'table': table,
        'restaurant': restaurant,
        'menu_types': menu_types,
        'has_active_order': active_order is not None
    }
    
    return render(request, 'table_service/menu.html', context)

def bill_view(request, table_uuid):
    """Страница с текущим счетом"""
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.section.restaurant
    
    # Получаем активный заказ
    active_order = Order.objects.filter(
        table=table, 
        status__in=['new', 'processing', 'ready', 'delivered']
    ).first()
    
    context = {
        'table': table,
        'restaurant': restaurant,
        'order': active_order
    }
    
    return render(request, 'table_service/bill.html', context)

@csrf_exempt 
@require_POST
def call_waiter(request, table_uuid):
    """API для вызова официанта"""
    table = get_object_or_404(Table, uuid=table_uuid)
    
    if not table.call_waiter:
        table.call_waiter = True
        table.call_time = timezone.now()
        table.save(update_fields=['call_waiter', 'call_time'])
        
        # Здесь может быть логика для уведомления официанта
        
        return JsonResponse({
            'success': True,
            'message': 'Официант вызван, он подойдет к вам в ближайшее время'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Официант уже вызван и скоро подойдет'
        })

@csrf_exempt 
@require_POST
def request_bill(request, table_uuid):
    """API для запроса счета"""
    table = get_object_or_404(Table, uuid=table_uuid)
    
    if not table.bill_waiter:
        table.bill_waiter = True
        table.bill_time = timezone.now()
        table.save(update_fields=['bill_waiter', 'bill_time'])
        
        # Здесь может быть логика для уведомления официанта
        
        return JsonResponse({
            'success': True, 
            'message': 'Запрос на счет отправлен'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Счет уже запрошен и скоро будет доставлен'
        })

@csrf_exempt 
def review_view(request, table_uuid):
    """Страница для оставления отзыва"""
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.section.restaurant
    
    context = {
        'table': table,
        'restaurant': restaurant
    }
    
    return render(request, 'table_service/review.html', context)

@require_GET
def menu_items_api(request, table_uuid):
    """API для получения элементов меню"""
    table = get_table_from_uuid(table_uuid)
    if not table:
        return JsonResponse({'error': 'Стол не найден'}, status=404)
    
    restaurant = table.section.restaurant
    
    menu_type_id = request.GET.get('menu_type_id')
    query = request.GET.get('q', '').strip()
    
    menu_items = Menu.objects.filter(restaurant=restaurant, is_available=True)
    
    if menu_type_id:
        menu_items = menu_items.filter(menu_type_id=menu_type_id)
    
    if query:
        menu_items = menu_items.filter(
            name_ru__icontains=query
        ) | menu_items.filter(
            name_kz__icontains=query
        )
    
    data = []
    for item in menu_items:
        data.append({
            'id': item.id,
            'name': item.name_ru,
            'name_kz': item.name_kz,
            'description': item.description_ru or '',
            'price': float(item.price),
            'image_url': item.image.url if item.image else None,
            'menu_type_id': item.menu_type_id,
            'calories': item.calories,
            'proteins': float(item.proteins) if item.proteins else None,
            'fats': float(item.fats) if item.fats else None,
            'carbohydrates': float(item.carbohydrates) if item.carbohydrates else None,
            'is_healthy': item.is_healthy()
        })
    
    return JsonResponse({'items': data})

@csrf_exempt 
@require_POST
def add_to_order(request, table_uuid):
    """API для добавления блюда в заказ"""
    try:
        table = get_object_or_404(Table, uuid=table_uuid)
        data = json.loads(request.body)
        
        menu_item_id = data.get('menu_item_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return HttpResponseBadRequest('Количество должно быть больше нуля')
        
        menu_item = get_object_or_404(Menu, id=menu_item_id, restaurant=table.section.restaurant)
        
        # Получение или создание активного заказа
        active_order = Order.objects.filter(
            table=table, 
            status__in=['new', 'processing']
        ).first()
        
        if not active_order:
            active_order = Order.objects.create(
                table=table,
                status='new',
                user=request.user if request.user.is_authenticated else None
            )
        
        # Добавление или обновление позиции заказа
        order_item, created = OrderItem.objects.get_or_create(
            order=active_order,
            menu_item=menu_item,
            defaults={
                'price': menu_item.price,
                'quantity': quantity
            }
        )
        
        if not created:
            order_item.quantity += quantity
            order_item.save(update_fields=['quantity'])
        
        # Пересчет общей стоимости заказа
        order_total = OrderItem.objects.filter(order=active_order).aggregate(
            total=Coalesce(Sum(F('price') * F('quantity')), 0, output_field=DecimalField())
        )['total']
        
        active_order.total_price = order_total
        active_order.save(update_fields=['total_price'])
        
        return JsonResponse({
            'success': True,
            'message': f'{menu_item.name_ru} добавлено в заказ',
            'order_total': float(active_order.total_price),
            'item_count': OrderItem.objects.filter(order=active_order).count(),
            'total_quantity': OrderItem.objects.filter(order=active_order).aggregate(
                total=Coalesce(Sum('quantity'), 0)
            )['total']
        })
    
    except Exception as e:
        logger.error(f"Error adding to order: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при добавлении в заказ'
        }, status=400)

@require_GET
def order_status(request, table_uuid):
    """API для получения статуса заказа"""
    table = get_object_or_404(Table, uuid=table_uuid)
    
    active_orders = Order.objects.filter(
        table=table, 
        status__in=['new', 'processing', 'ready', 'delivered']
    )
    
    if not active_orders:
        return JsonResponse({
            'has_order': False,
            'message': 'У этого стола нет активных заказов'
        })
    
    order_data = []
    
    for order in active_orders:
        items = []
        
        for item in order.items.all():
            items.append({
                'id': item.id,
                'name': item.menu_item.name_ru,
                'price': float(item.price),
                'quantity': item.quantity,
                'total': float(item.price * item.quantity)
            })
        
        order_data.append({
            'id': order.id,
            'status': order.get_status_display(),
            'status_code': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total': float(order.total_price),
            'items': items
        })
    
    return JsonResponse({
        'has_order': True,
        'orders': order_data
    })

@csrf_exempt 
@require_POST
def submit_review(request, table_uuid):
    """API для отправки отзыва"""
    try:
        table = get_object_or_404(Table, uuid=table_uuid)
        restaurant = table.section.restaurant
        data = json.loads(request.body)
        
        rating = int(data.get('rating', 5))
        comment = data.get('comment', '')
        
        if rating < 1 or rating > 5:
            return HttpResponseBadRequest('Оценка должна быть от 1 до 5')
        
        # Создаем анонимный отзыв, если пользователь не авторизован
        review = Review.objects.create(
            restaurant=restaurant,
            user=request.user if request.user.is_authenticated else None,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Спасибо за ваш отзыв!',
            'review_id': review.id
        })
    
    except Exception as e:
        logger.error(f"Error submitting review: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при отправке отзыва'
        }, status=400)