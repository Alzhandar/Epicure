from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferItemViewSet, OfferReservationViewSet

app_name = 'offers'

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'offer-items', OfferItemViewSet, basename='offer-item')
router.register(r'reservations', OfferReservationViewSet, basename='reservation')

urlpatterns = router.urls