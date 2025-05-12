from django.db import models
from django.utils.translation import gettext_lazy as _
from restaurant.models import Restaurant, Table
from users.models import User


class OfferType(models.TextChoices):
    ROMANTIC = 'romantic', _('Романтический')
    FAMILY = 'family', _('Семейный')
    BUSINESS = 'business', _('Бизнес')
    CELEBRATION = 'celebration', _('Праздничный')
    SPECIAL = 'special', _('Специальный')


class Offer(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name='Ресторан'
    )
    title_ru = models.CharField(
        max_length=100,
        verbose_name='Название (Русский)'
    )
    title_kz = models.CharField(
        max_length=100,
        verbose_name='Название (Казахский)',
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='offers/images/',
        verbose_name='Фото предложения'
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Старая цена'
    )
    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Новая цена'
    )
    badge = models.CharField(
        max_length=50,
        verbose_name='Значок предложения',
        help_text='Например: "Хит", "-20%", "Быстро"'
    )
    people_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество человек',
        help_text='На сколько человек рассчитано предложение'
    )
    per_person = models.BooleanField(
        default=False,
        verbose_name='Цена за человека',
        help_text='Указывать ли цену за человека или за всё предложение'
    )
    offer_type = models.CharField(
        max_length=20,
        choices=OfferType.choices,
        default=OfferType.SPECIAL,
        verbose_name='Тип предложения'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return f"{self.title_ru} - {self.restaurant.name}"

    class Meta:
        verbose_name = 'Пакетное предложение'
        verbose_name_plural = 'Пакетные предложения'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant', 'offer_type']),
            models.Index(fields=['is_active']),
        ]


class OfferItem(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Предложение'
    )
    description_ru = models.CharField(
        max_length=255,
        verbose_name='Описание элемента (Русский)'
    )
    description_kz = models.CharField(
        max_length=255,
        verbose_name='Описание элемента (Казахский)',
        blank=True,
        null=True
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок отображения'
    )

    def __str__(self):
        return f"{self.description_ru}"

    class Meta:
        verbose_name = 'Элемент предложения'
        verbose_name_plural = 'Элементы предложения'
        ordering = ['order']


class OfferReservation(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Предложение'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offer_reservations',
        verbose_name='Пользователь'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        related_name='offer_reservations',
        verbose_name='Зарезервированный стол',
        null=True,
        blank=True
    )
    date = models.DateField(
        verbose_name='Дата бронирования'
    )
    time = models.TimeField(
        verbose_name='Время бронирования'
    )
    guest_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество гостей'
    )
    special_requests = models.TextField(
        blank=True,
        null=True,
        verbose_name='Особые пожелания'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает подтверждения'),
            ('confirmed', 'Подтверждено'),
            ('completed', 'Завершено'),
            ('cancelled', 'Отменено'),
        ],
        default='pending',
        verbose_name='Статус бронирования'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return f"{self.offer.title_ru} - {self.date} {self.time}"

    class Meta:
        verbose_name = 'Бронирование предложения'
        verbose_name_plural = 'Бронирования предложений'
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['offer', 'date']),
            models.Index(fields=['user', 'status']),
        ]