from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, SectionViewSet, TableViewSet

router = DefaultRouter()
router.register(r'', RestaurantViewSet, basename='restaurant')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'tables', TableViewSet, basename='table')

urlpatterns = router.urls