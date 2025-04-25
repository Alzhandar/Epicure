from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reservations', views.ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
    path('availability/', views.TableAvailabilityView.as_view(), name='table-availability'),
    path('available-times/', views.AvailableTimeSlotsView.as_view(), name='available-times'),
    path('check-conflict/', views.CheckReservationConflictView.as_view(), name='check-conflict'),
    path('restaurant/<int:restaurant_id>/tables/', views.RestaurantTablesView.as_view(), name='restaurant-tables'),
    path('cancel/<int:pk>/', views.CancelReservationView.as_view(), name='cancel-reservation'),
    path('confirm/<int:pk>/', views.ConfirmReservationView.as_view(), name='confirm-reservation'),
    path('complete/<int:pk>/', views.CompleteReservationView.as_view(), name='complete-reservation'),
    path('no-show/<int:pk>/', views.NoShowReservationView.as_view(), name='no-show-reservation'),
]