from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

import logging
from datetime import timedelta

from .models import Notification, NotificationType, NotificationStatus
from room.models import Reservation, ReservationStatus

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def create_notification(recipient_email, title, message, notification_type, 
                           reservation=None, recipient_phone=None, user=None):
        try:
            notification = Notification.objects.create(
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                title=title,
                message=message,
                notification_type=notification_type,
                reservation=reservation,
                user=user
            )
            logger.info(f"Создано уведомление: {notification.id} - {notification_type}")
            return notification
        except Exception as e:
            logger.error(f"Ошибка при создании уведомления: {str(e)}")
            return None

    @staticmethod
    def send_welcome_notification(user):
        if not user.email:
            logger.warning(f"Не удалось отправить приветственное уведомление: отсутствует email для пользователя {user.username}")
            return None
        
        title = "Добро пожаловать в Epicure!"
        message = f"""
        Уважаемый(ая) {user.username},
        
        Мы рады приветствовать вас на нашей платформе Epicure! Теперь вы можете:
        
        • Бронировать столики в лучших ресторанах
        • Изучать меню до своего визита
        • Получать персональные рекомендации
        • Накапливать бонусы за каждое посещение
        
        Не стесняйтесь обращаться к нам, если у вас возникнут вопросы.
        
        С наилучшими пожеланиями,
        Команда Epicure
        """
        
        notification = NotificationService.create_notification(
            recipient_email=user.email,
            recipient_phone=getattr(user, 'phone_number', None),
            title=title,
            message=message,
            notification_type=NotificationType.WELCOME,
            user=user
        )
        
        if notification:
            NotificationService.send_email_notification(notification)
        
        return notification

    @staticmethod
    def send_payment_success_notification(reservation):
        if not reservation.guest_email:
            logger.warning(f"Не удалось отправить уведомление об оплате: отсутствует email для бронирования {reservation.id}")
            return None
        
        title = "Ваш платеж успешно обработан"
        message = f"""
        Уважаемый(ая) {reservation.guest_name},
        
        Благодарим вас за оплату вашего бронирования в ресторане {reservation.restaurant.name}.
        
        Детали бронирования:
        - Дата: {reservation.reservation_date}
        - Время: {reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')}
        - Количество гостей: {reservation.guest_count}
        - Стол: №{reservation.table.number}
        
        С нетерпением ждём вашего визита!
        
        С уважением,
        Команда Epicure
        """
        
        notification = NotificationService.create_notification(
            recipient_email=reservation.guest_email,
            recipient_phone=reservation.guest_phone,
            title=title,
            message=message,
            notification_type=NotificationType.PAYMENT_SUCCESS,
            reservation=reservation
        )
        
        if notification:
            NotificationService.send_email_notification(notification)
        
        return notification
    
    @staticmethod
    def send_reservation_reminder_notifications():
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        reservations = Reservation.objects.filter(
            reservation_date=tomorrow,
            status=ReservationStatus.CONFIRMED
        )
        
        sent_count = 0
        for reservation in reservations:
            if not reservation.guest_email:
                continue
            
            title = "Напоминание о вашем бронировании завтра"
            message = f"""
            Уважаемый(ая) {reservation.guest_name},
            
            Напоминаем вам о бронировании в ресторане {reservation.restaurant.name} завтра.
            
            Детали бронирования:
            - Дата: {reservation.reservation_date}
            - Время: {reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')}
            - Количество гостей: {reservation.guest_count}
            - Стол: №{reservation.table.number}
            
            С нетерпением ждём вашего визита!
            
            С уважением,
            Команда Epicure
            """
            
            notification = NotificationService.create_notification(
                recipient_email=reservation.guest_email,
                recipient_phone=reservation.guest_phone,
                title=title,
                message=message,
                notification_type=NotificationType.RESERVATION_REMINDER,
                reservation=reservation
            )
            
            if notification and NotificationService.send_email_notification(notification):
                sent_count += 1
        
        logger.info(f"Отправлено {sent_count} напоминаний о бронировании на завтра")
        return sent_count

    @staticmethod
    def send_email_notification(notification):
        try:
            context = {
                'title': notification.title,
                'message': notification.message,
                'notification_id': notification.id,
                'notification_type': notification.notification_type
            }
            
            if notification.notification_type == NotificationType.WELCOME:
                context['site_url'] = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
            
            elif notification.notification_type == NotificationType.PAYMENT_SUCCESS and notification.reservation:
                context['site_url'] = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
                context['reservation_id'] = notification.reservation.id
            
            html_message = render_to_string(
                'notifications/email_template.html',
                context
            )
            plain_message = strip_tags(html_message)
            
            if settings.DEBUG and settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                send_mail(
                    subject=notification.title,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.recipient_email],
                    html_message=html_message,
                    fail_silently=True,
                )
            else:
                send_mail(
                    subject=notification.title,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.recipient_email],
                    html_message=html_message,
                    fail_silently=False,
                )
            
            notification.mark_as_sent()
            logger.info(f"Отправлено email-уведомление: {notification.id}")
            return True
            
        except Exception as e:
            notification.mark_as_failed()
            logger.error(f"Ошибка при отправке email-уведомления {notification.id}: {str(e)}")
            
            if settings.DEBUG:
                notification.mark_as_sent()
                return True
            
            return False