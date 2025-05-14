from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StripePayment
from room.models import Reservation
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
                    success_url=f'{domain}/success',
                    cancel_url=f'{domain}/cancelled',
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
        
        
        

class PaymentSuccessView(APIView):
    """
    API View to handle successful Stripe payments.
    This endpoint verifies the payment session and updates the reservation status.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Retrieve the session to verify its status
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                logger.warning(f"Payment not completed for session {session_id}")
                return Response({'error': 'Payment has not been completed'}, status=400)
            
            # Get the payment object using metadata from the session
            payment_id = session.metadata.get('payment_id')
            reservation_id = session.metadata.get('reservation_id')
            
            try:
                payment = StripePayment.objects.get(id=payment_id)
            except StripePayment.DoesNotExist:
                logger.error(f"Payment {payment_id} not found")
                return Response({'error': 'Payment record not found'}, status=404)
            
            # Update payment status
            payment.status = 'completed'
            payment.payment_date = timezone.now()
            payment.save()
            
            # Update reservation status
            reservation = payment.reservation
            reservation.payment_status = 'paid'
            reservation.save()
            
            # Email sending code removed
            
            return Response({
                'status': 'success',
                'message': 'Payment processed successfully',
                'reservation_id': reservation.id,
                'payment_id': payment.id,
                'amount': payment.amount,
                'currency': payment.currency
            })
            
        except stripe.error.StripeError as stripe_error:
            logger.error(f"Stripe Error in success handling: {stripe_error}")
            return Response({'error': 'Payment verification failed', 'details': str(stripe_error)}, status=400)
        
        except Exception as e:
            logger.error(f"Unexpected error in payment success: {e}", exc_info=True)
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)


class PaymentCancelView(APIView):
    """
    API View to handle canceled Stripe payments.
    This endpoint ensures payments are properly marked as 'Canceled' in Stripe.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        # If no session_id provided, we'll still handle it
        if session_id:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                
                # 1. Retrieve the Stripe session
                session = stripe.checkout.Session.retrieve(session_id)
                
                # 2. Cancel the payment intent (this will show as "Canceled" in the dashboard)
                if hasattr(session, 'payment_intent') and session.payment_intent:
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    
                    # Only cancel if it's in a state that can be canceled
                    if payment_intent.status in ['requires_payment_method', 'requires_capture', 'requires_confirmation', 'requires_action', 'processing']:
                        # This is what creates the "Canceled" status in the Stripe dashboard
                        stripe.PaymentIntent.cancel(payment_intent.id)
                        logger.info(f"Payment intent {payment_intent.id} has been canceled")
                
                # 3. Also expire the checkout session if it's still open
                if session.status == 'open':
                    stripe.checkout.Session.expire(session_id)
                    logger.info(f"Session {session_id} has been expired")
                
                # 4. Update our database
                payment_id = session.metadata.get('payment_id')
                if payment_id:
                    try:
                        payment = StripePayment.objects.get(id=payment_id)
                        payment.status = 'canceled'
                        payment.canceled_at = timezone.now()
                        payment.save()
                        
                        # Update the reservation status
                        reservation = payment.reservation
                        reservation.payment_status = 'unpaid'
                        reservation.save()
                        
                        logger.info(f"Payment {payment_id} marked as canceled in database")
                    except StripePayment.DoesNotExist:
                        logger.warning(f"Payment {payment_id} not found for cancellation")
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error when canceling payment: {e}")
            except Exception as e:
                logger.error(f"Error handling payment cancellation: {e}", exc_info=True)
        
        return Response({
            'status': 'canceled',
            'message': 'Payment was canceled'
        })