from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, GuestNotificationsView

app_name = 'notifications'

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('guest/', GuestNotificationsView.as_view(), name='guest-notifications'),
]