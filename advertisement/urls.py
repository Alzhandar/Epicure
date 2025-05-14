from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import banner_click, banner_impression, BannerViewSet

app_name = 'advertisement'

router = DefaultRouter()
router.register('banners', BannerViewSet)

urlpatterns = [
    path('', include((router.urls, app_name), namespace='api')),
    path('banner/<int:banner_id>/click/', banner_click, name='banner_click'),
    path('banner/<int:banner_id>/impression/', banner_impression, name='banner_impression'),
]