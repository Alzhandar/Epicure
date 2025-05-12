from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StripePayment
from room.models import Reservation, ReservationMenuItem
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reservation_id = request.data.get('reservation_id')

        try:
            reservation = Reservation.objects.get(id=reservation_id, table__section__restaurant__isnull=False)

            if reservation.guest_email is None:
                return Response({'error': 'Guest email is required for payment.'}, status=400)

            items = ReservationMenuItem.objects.filter(reservation=reservation)
            if not items.exists():
                return Response({'error': 'No menu items attached to reservation.'}, status=400)

            total_amount = sum(item.menu_item.price * item.quantity for item in items)
            total_cents = int(total_amount * Decimal('100'))

            # Create StripePayment record
            payment = StripePayment.objects.create(
                user=request.user,
                reservation=reservation,
                amount=total_amount,
                currency='USD',
                status='pending'
            )

            # Get frontend URL from settings
            domain = settings.FRONTEND_BASE_URL  # e.g., http://localhost:3000

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': payment.currency.lower(),
                        'product_data': {
                            'name': f'Reservation #{reservation.id} - Menu Order',
                        },
                        'unit_amount': total_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                metadata={
                    'reservation_id': reservation.id,
                    'payment_id': payment.id
                },
                customer_email=reservation.guest_email,
                success_url=f'{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{domain}/payment-cancel',
            )

            # Save Stripe session ID (or payment intent) for later verification
            payment.stripe_payment_intent_id = session.payment_intent or session.id
            payment.save()

            return Response({'checkout_url': session.url})

        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found or invalid'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)