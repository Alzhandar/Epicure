from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
]