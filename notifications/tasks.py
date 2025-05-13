import logging
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import transaction

from .models import Notification, NotificationStatus
from .services import NotificationService
from room.models import Reservation, ReservationStatus

logger = logging.getLogger(__name__)


def send_reservation_reminders():
    logger.info("Запущена задача отправки напоминаний о бронированиях")
    try:
        NotificationService.send_reservation_reminder_notifications()
        logger.info("Задача отправки напоминаний завершена успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {str(e)}")
        return False


def resend_failed_notifications():
    logger.info("Запущена задача повторной отправки неудачных уведомлений")
    try:
        threshold = timezone.now() - timedelta(days=3)
        notifications = Notification.objects.filter(
            status=NotificationStatus.FAILED,
            created_at__gte=threshold
        )
        
        sent_count = 0
        for notification in notifications:
            if NotificationService.send_email_notification(notification):
                sent_count += 1
        
        logger.info(f"Повторно отправлено {sent_count} из {notifications.count()} уведомлений")
        return True
    except Exception as e:
        logger.error(f"Ошибка при повторной отправке уведомлений: {str(e)}")
        return False


def clean_old_notifications():
    logger.info("Запущена задача очистки старых уведомлений")
    try:
        threshold = timezone.now() - timedelta(days=60)
        count, _ = Notification.objects.filter(
            created_at__lt=threshold
        ).delete()
        
        logger.info(f"Удалено {count} старых уведомлений")
        return True
    except Exception as e:
        logger.error(f"Ошибка при очистке старых уведомлений: {str(e)}")
        return False