from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

router = DefaultRouter()
router.register(r'menu-items', views.MenuViewSet, basename='menu-item')
router.register(r'menu-types', views.MenuTypeViewSet, basename='menu-type')

urlpatterns = [
    path('dish/<int:dish_id>/', views.get_dish_details, name='dish_details'),
    path('', include(router.urls)),
]