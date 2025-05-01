from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserViewSet, UserRegistrationView, ProfileViewSet

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mobile/profile/', ProfileViewSet.as_view({'get': 'me'}), name='mobile-profile'),
    path('profile/update/', ProfileViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='mobile-profile-update'),
    path('profile/avatar/', ProfileViewSet.as_view({'post': 'upload_avatar'}), name='mobile-profile-avatar'),
    path('profile/password/', ProfileViewSet.as_view({'post': 'change_password'}), name='mobile-profile-password'),
    path('profile/language/', ProfileViewSet.as_view({'post': 'update_language'}), name='mobile-profile-language'),
    path('', include(router.urls)),
]