from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, 
)

from .views import UserViewSet, UserRegistrationView, ProfileViewSet

router = DefaultRouter()
router.register(r'', UserViewSet)

profile_router = DefaultRouter()
profile_router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), 
    path('', include(profile_router.urls)), 
    path('', include(router.urls)),
]