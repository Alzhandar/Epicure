from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, SectionViewSet, TableViewSet, ReviewViewSet

app_name = 'restaurant'

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')

urlpatterns = [
    path('', include(router.urls)),
]