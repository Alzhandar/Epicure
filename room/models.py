from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from restaurant.models import Restaurant, Section, Table
from products.models import Menu


class ReservationStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает подтверждения'
    CONFIRMED = 'confirmed', 'Подтверждено'
    CANCELLED = 'cancelled', 'Отменено'
    COMPLETED = 'completed', 'Завершено'
    NO_SHOW = 'no_show', 'Неявка'


class Reservation(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Ресторан'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Стол'
    )
    reservation_date = models.DateField(
        verbose_name='Дата бронирования'
    )
    start_time = models.TimeField(
        verbose_name='Время начала'
    )
    end_time = models.TimeField(
        verbose_name='Время окончания'
    )
    guest_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Количество гостей'
    )
    guest_name = models.CharField(
        max_length=255,
        verbose_name='Имя клиента'
    )
    guest_phone = models.CharField(
        max_length=20,
        verbose_name='Телефон клиента'
    )
    guest_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='Email клиента'
    )
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        verbose_name='Статус бронирования'
    )
    special_requests = models.TextField(
        null=True,
        blank=True,
        verbose_name='Особые пожелания'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-reservation_date', '-start_time']
        indexes = [
            models.Index(fields=['reservation_date', 'start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['table', 'reservation_date']),
        ]

    def __str__(self):
        return f"{self.guest_name} - {self.restaurant.name} - Стол №{self.table.number} - {self.reservation_date}"

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Время окончания должно быть позже времени начала')
        
        if self.reservation_date and self.reservation_date < timezone.now().date():
            raise ValidationError('Нельзя создать бронирование на прошедшую дату')

        if self.table and self.reservation_date and self.start_time and self.end_time:
            conflicting_reservations = Reservation.objects.filter(
                table=self.table,
                reservation_date=self.reservation_date,
                status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED]
            ).exclude(pk=self.pk)
            
            for reservation in conflicting_reservations:
                if ((self.start_time <= reservation.start_time < self.end_time) or
                    (self.start_time < reservation.end_time <= self.end_time) or
                    (reservation.start_time <= self.start_time < reservation.end_time) or
                    (self.start_time <= reservation.start_time and self.end_time >= reservation.end_time)):
                    raise ValidationError(f'Конфликт бронирования: стол уже забронирован с {reservation.start_time} до {reservation.end_time}')
                    
        # Проверка, что стол принадлежит указанному ресторану
        if self.table and self.restaurant and self.table.section and self.table.section.restaurant != self.restaurant:
            raise ValidationError('Выбранный стол не принадлежит указанному ресторану')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ReservationMenuItem(models.Model):
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='Бронирование'
    )
    menu_item = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='reservation_items',
        verbose_name='Блюдо'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    
    class Meta:
        verbose_name = 'Блюдо для бронирования'
        verbose_name_plural = 'Блюда для бронирования'
        unique_together = ['reservation', 'menu_item']
    
    def __str__(self):
        return f"{self.menu_item.name_ru} x{self.quantity} для {self.reservation}"