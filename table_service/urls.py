from django.urls import path
from . import views

app_name = 'table_service'

urlpatterns = [
    path('', views.table_service_view, name='table_service'),
    path('menu/', views.menu_view, name='menu'),
    path('bill/', views.bill_view, name='bill'),
    path('call-waiter/', views.call_waiter, name='call_waiter'),
    path('request-bill/', views.request_bill, name='request_bill'),
    path('review/', views.review_view, name='review'),
    
    path('api/menu-items/', views.menu_items_api, name='api_menu_items'),
    path('api/add-to-order/', views.add_to_order, name='api_add_to_order'),
    path('api/order-status/', views.order_status, name='api_order_status'),
    path('api/submit-review/', views.submit_review, name='api_submit_review'),
]