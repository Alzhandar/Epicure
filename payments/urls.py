from django.urls import path
from .views import CreateCheckoutSessionView, PaymentCancelView, PaymentSuccessView


urlpatterns = [
    path('checkout/', CreateCheckoutSessionView.as_view(), name='checkout-session'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
]