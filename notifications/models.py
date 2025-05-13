from django.db import models
from django.conf import settings
from django.utils import timezone

from room.models import Reservation


class NotificationType(models.TextChoices):
    PAYMENT_SUCCESS = 'payment_success', 'Успешная оплата'
    RESERVATION_REMINDER = 'reservation_reminder', 'Напоминание о бронировании'
    RESERVATION_CREATED = 'reservation_created', 'Бронирование создано'
    RESERVATION_CANCELED = 'reservation_canceled', 'Бронирование отменено'
    RESERVATION_CONFIRMED = 'reservation_confirmed', 'Бронирование подтверждено'


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'В ожидании'
    SENT = 'sent', 'Отправлено'
    READ = 'read', 'Прочитано'
    FAILED = 'failed', 'Ошибка'


class Notification(models.Model):
    recipient_email = models.EmailField(verbose_name='Email получателя')
    recipient_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон получателя')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(
        max_length=30, 
        choices=NotificationType.choices,
        verbose_name='Тип уведомления'
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name='Статус уведомления'
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name='Бронирование'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата прочтения')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification_type']),
            models.Index(fields=['status']),
            models.Index(fields=['recipient_email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.recipient_email}"
    
    def mark_as_read(self):
        self.status = NotificationStatus.READ
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_sent(self):
        self.status = NotificationStatus.SENT
        self.save()
    
    def mark_as_failed(self):
        self.status = NotificationStatus.FAILED
        self.save()