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
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY


logger = logging.getLogger(__name__)

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reservation_id = request.data.get('reservation_id')

        if not reservation_id:
            return Response({'error': 'Reservation ID is required'}, status=400)

        try:
            try:
                reservation = Reservation.objects.select_related(
                    'restaurant',
                    'table',
                    'table__section'
                ).prefetch_related(
                    'menu_items__menu_item'
                ).get(id=reservation_id)
            except Reservation.DoesNotExist:
                logger.error(f"Reservation {reservation_id} not found")
                return Response({'error': 'Reservation not found'}, status=404)

            menu_items = reservation.menu_items.all()

            if not reservation.guest_email:
                logger.warning(f"Reservation {reservation_id} lacks guest email")
                return Response({'error': 'Guest email is required for payment.'}, status=400)

            if not menu_items.exists():
                logger.warning(f"Reservation {reservation_id} has no menu items")
                return Response({'error': 'No menu items attached to reservation.'}, status=400)

            line_items = []

            # Add menu items as line items (without "Quantity:" in description)
            for item in menu_items:
                line_items.append({
                    'price_data': {
                        'currency': 'kzt',
                        'product_data': {
                            'name': f"{item.menu_item.name_ru}"
                        },
                        'unit_amount': int(item.menu_item.price * Decimal('100'))
                    },
                    'quantity': item.quantity,
                })

            # Readable reservation details with line breaks
            reservation_details_name = f"Reservation #{reservation.id}"
            reservation_details_description = (
                f"• Date: {reservation.reservation_date.strftime('%Y-%m-%d')} | "
                f"Time: {reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')} | "
                f"Guests: {reservation.guest_count} | "
                f"Table: #{reservation.table.number} "
                f"({reservation.table.section.name if reservation.table.section else 'No Section'}) | "
                f"Restaurant: {reservation.restaurant.name}"
              )
            

            # Add reservation details as a zero-cost item
            line_items.append({
                'price_data': {
                    'currency': 'kzt',
                    'product_data': {
                        'name': reservation_details_name,
                        'description': reservation_details_description
                    },
                    'unit_amount': 0
                },
                'quantity': 1,
            })

            total_amount = sum(item.menu_item.price * item.quantity for item in menu_items)
            total_cents = int(total_amount * Decimal('100'))

            if total_amount <= 0:
                logger.error(f"Invalid total amount for reservation {reservation_id}: {total_amount}")
                return Response({'error': 'Invalid payment amount'}, status=400)

            payment = StripePayment.objects.create(
                user=request.user,
                reservation=reservation,
                amount=total_amount,
                currency='KZT',
                status='pending'
            )

            domain = settings.FRONTEND_BASE_URL
            stripe.api_key = settings.STRIPE_SECRET_KEY

            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    metadata={
                        'reservation_id': str(reservation.id),
                        'payment_id': str(payment.id)
                    },
                    customer_email=reservation.guest_email,
                    success_url=f'{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
                    cancel_url=f'{domain}/payment-cancel',
                )

                payment.stripe_payment_intent_id = session.payment_intent or session.id
                payment.save()

                logger.info(f"Stripe Checkout Session created successfully: {session.id}")

                menu_item_details = [{
                    'menu_item_id': item.menu_item.id,
                    'name': item.menu_item.name_ru,
                    'price': item.menu_item.price,
                    'quantity': item.quantity,
                    'total_price': item.menu_item.price * item.quantity
                } for item in menu_items]

                return Response({
                    'checkout_url': session.url,
                    'session_id': session.id,
                    'menu_items': menu_item_details,
                    'total_amount': total_amount,
                    'reservation_details': {
                        'id': reservation.id,
                        'date': reservation.reservation_date,
                        'start_time': reservation.start_time,
                        'end_time': reservation.end_time,
                        'guest_count': reservation.guest_count,
                        'table_number': reservation.table.number,
                        'section_name': reservation.table.section.name if reservation.table.section else None,
                        'restaurant_name': reservation.restaurant.name
                    }
                })

            except stripe.error.StripeError as stripe_error:
                logger.error(f"Stripe Error: {stripe_error}")
                return Response({'error': 'Payment processing failed', 'details': str(stripe_error)}, status=400)

        except Exception as e:
            logger.error(f"Unexpected error in checkout: {e}", exc_info=True)
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)
