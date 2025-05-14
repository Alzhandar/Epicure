from django.urls import path
from . import views

app_name = 'table_service'

urlpatterns = [
    # Основные страницы
    path('<uuid:table_uuid>/', views.table_service_view, name='table_service'),
    path('<uuid:table_uuid>/menu/', views.menu_view, name='menu'),
    path('<uuid:table_uuid>/bill/', views.bill_view, name='bill'),
    path('<uuid:table_uuid>/review/', views.review_view, name='review'),
    
    # API endpoints
    path('<uuid:table_uuid>/call-waiter/', views.call_waiter, name='call_waiter'),
    path('<uuid:table_uuid>/request-bill/', views.request_bill, name='request_bill'),
    path('<uuid:table_uuid>/api/menu-items/', views.menu_items_api, name='api_menu_items'),
    path('<uuid:table_uuid>/api/add-to-order/', views.add_to_order, name='api_add_to_order'),
    path('<uuid:table_uuid>/api/order-status/', views.order_status, name='api_order_status'),
    path('<uuid:table_uuid>/api/submit-review/', views.submit_review, name='api_submit_review'),
]