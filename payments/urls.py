from django.urls import path, include
from .views import CreateCheckoutSessionView


urlpatterns = [
    path('checkout/', CreateCheckoutSessionView.as_view(), name='checkout-session'),
]