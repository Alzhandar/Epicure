import logging
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from .models import Notification, NotificationStatus, NotificationType
from .services import NotificationService
from room.models import Reservation, ReservationStatus

logger = logging.getLogger(__name__)


def send_reservation_reminders():
    logger.info("Запущена задача отправки напоминаний о бронированиях")
    start_time = timezone.now()
    try:
        with transaction.atomic():
            sent_count = NotificationService.send_reservation_reminder_notifications()
            
        execution_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Задача отправки напоминаний завершена успешно. Отправлено {sent_count} напоминаний за {execution_time:.2f} сек")
        return {"success": True, "sent_count": sent_count, "execution_time": execution_time}
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {str(e)}")
        return {"success": False, "error": str(e)}


def resend_failed_notifications():
    logger.info("Запущена задача повторной отправки неудачных уведомлений")
    start_time = timezone.now()
    try:
        threshold = timezone.now() - timedelta(days=3)
        notifications = Notification.objects.filter(
            status=NotificationStatus.FAILED,
            created_at__gte=threshold
        )
        
        total_count = notifications.count()
        if total_count == 0:
            logger.info("Нет неудачных уведомлений для повторной отправки")
            return {"success": True, "sent_count": 0, "total_count": 0}
        
        sent_count = 0
        for notification in notifications:
            if NotificationService.send_email_notification(notification):
                sent_count += 1
        
        execution_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Повторно отправлено {sent_count} из {total_count} уведомлений за {execution_time:.2f} сек")
        return {"success": True, "sent_count": sent_count, "total_count": total_count, "execution_time": execution_time}
    
    except Exception as e:
        logger.error(f"Ошибка при повторной отправке уведомлений: {str(e)}")
        return {"success": False, "error": str(e)}


def clean_old_notifications():
    logger.info("Запущена задача очистки старых уведомлений")
    start_time = timezone.now()
    try:
        threshold = timezone.now() - timedelta(days=90)
        result = Notification.objects.filter(
            created_at__lt=threshold
        ).delete()
        
        count = result[0] if isinstance(result, tuple) and len(result) > 0 else 0
        
        execution_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Удалено {count} старых уведомлений за {execution_time:.2f} сек")
        return {"success": True, "deleted_count": count, "execution_time": execution_time}
    
    except Exception as e:
        logger.error(f"Ошибка при очистке старых уведомлений: {str(e)}")
        return {"success": False, "error": str(e)}


def send_daily_summary_to_users():
    logger.info("Запущена задача отправки дневных сводок пользователям")
    start_time = timezone.now()
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        week_ahead = tomorrow + timedelta(days=6)
        
        users_with_reservations = User.objects.filter(
            Q(email__isnull=False) & 
            ~Q(email='') & 
            Q(is_active=True) &
            Q(reservations__reservation_date__range=[tomorrow, week_ahead]) &
            ~Q(reservations__status=ReservationStatus.CANCELLED)
        ).distinct()
        
        sent_count = 0
        for user in users_with_reservations:
            reservations = Reservation.objects.filter(
                user=user,
                reservation_date__range=[tomorrow, week_ahead],
                status__in=[ReservationStatus.CONFIRMED, ReservationStatus.PENDING]
            ).order_by('reservation_date', 'start_time')[:5]  # Ограничиваем до 5 бронирований для сводки
            
            if reservations:
                title = "Ваши предстоящие бронирования"
                
                message = f"""
                Уважаемый(ая) {user.username},
                
                Вот ваши предстоящие бронирования:
                """
                
                for reservation in reservations:
                    message += f"""
                    
                    {reservation.reservation_date} в {reservation.start_time.strftime('%H:%M')}
                    Ресторан: {reservation.restaurant.name}
                    Количество гостей: {reservation.guest_count}
                    Статус: {reservation.get_status_display()}
                    """
                
                message += """
                
                Для получения дополнительной информации или изменения бронирования, перейдите в раздел "Мои бронирования" в личном кабинете.
                
                С уважением,
                Команда Epicure
                """
                
                notification = NotificationService.create_notification(
                    recipient_email=user.email,
                    title=title,
                    message=message,
                    notification_type=NotificationType.RESERVATION_REMINDER,
                    user=user
                )
                
                if notification and NotificationService.send_email_notification(notification):
                    sent_count += 1
        
        execution_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Отправлено {sent_count} дневных сводок пользователям за {execution_time:.2f} сек")
        return {"success": True, "sent_count": sent_count, "execution_time": execution_time}
    
    except Exception as e:
        logger.error(f"Ошибка при отправке дневных сводок: {str(e)}")
        return {"success": False, "error": str(e)}