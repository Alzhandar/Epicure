from django.db import models
from django.core.validators import MinValueValidator
from restaurant.models import Restaurant, Section
from products.models import Menu


class RoomType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название типа комнаты'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание типа комнаты'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип комнаты'
        verbose_name_plural = 'Типы комнат'
        ordering = ['name']


class BookingType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Тип бронирования'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание типа бронирования'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип бронирования'
        verbose_name_plural = 'Типы бронирования'
        ordering = ['name']


class Room(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название комнаты'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='Ресторан'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        related_name='rooms',
        null=True,
        blank=True,
        verbose_name='Секция'
    )
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.SET_NULL,
        related_name='rooms',
        null=True,
        blank=True,
        verbose_name='Тип комнаты'
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Вместимость (человек)'
    )
    area = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Площадь (кв.м)'
    )
    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за час',
        help_text='Стоимость аренды комнаты за час'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание комнаты'
    )
    features = models.TextField(
        null=True,
        blank=True,
        verbose_name='Особенности и удобства',
        help_text='Перечислите особенности комнаты (проектор, звуковое оборудование и т.д.)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Отметьте, если комната доступна для бронирования'
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
        return f"{self.name} ({self.restaurant.name})"

    class Meta:
        verbose_name = 'Комната для мероприятий'
        verbose_name_plural = 'Комнаты для мероприятий'
        ordering = ['restaurant', 'name']
        indexes = [
            models.Index(fields=['restaurant', 'name']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['restaurant', 'name']


class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Комната'
    )
    image = models.ImageField(
        upload_to='rooms/images/',
        verbose_name='Фотография'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Главное фото',
        help_text='Отметьте, если это главное фото комнаты'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    def __str__(self):
        return f"Фото {self.id} комнаты {self.room.name}"

    class Meta:
        verbose_name = 'Фотография комнаты'
        verbose_name_plural = 'Фотографии комнат'
        ordering = ['-is_main', '-created_at']


class Package(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название пакета'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name='Комната'
    )
    booking_type = models.ForeignKey(
        BookingType,
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name='Тип мероприятия'
    )
    description = models.TextField(
        verbose_name='Описание пакета'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость пакета',
        help_text='Полная стоимость пакета (включая блюда)'
    )
    min_guests = models.PositiveIntegerField(
        default=1,
        verbose_name='Минимальное количество гостей'
    )
    max_guests = models.PositiveIntegerField(
        verbose_name='Максимальное количество гостей'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
        help_text='Отметьте, если пакет доступен для бронирования'
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
        return f"{self.name} - {self.room.name} ({self.booking_type.name})"

    class Meta:
        verbose_name = 'Пакет услуг'
        verbose_name_plural = 'Пакеты услуг'
        ordering = ['room', 'name']
        indexes = [
            models.Index(fields=['room', 'booking_type']),
            models.Index(fields=['is_active']),
        ]


class PackageMenu(models.Model):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='Пакет услуг'
    )
    menu_item = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='package_menus',
        verbose_name='Блюдо'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )
    notes = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Примечания'
    )

    def __str__(self):
        return f"{self.menu_item.name_ru} ({self.quantity} шт.) - {self.package.name}"

    class Meta:
        verbose_name = 'Блюдо в пакете'
        verbose_name_plural = 'Блюда в пакете'
        ordering = ['package', 'menu_item__name_ru']
        unique_together = ['package', 'menu_item']


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Комната'
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        related_name='bookings',
        null=True,
        blank=True,
        verbose_name='Выбранный пакет'
    )
    booking_type = models.ForeignKey(
        BookingType,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Тип мероприятия'
    )
    client_name = models.CharField(
        max_length=255,
        verbose_name='Имя клиента'
    )
    client_phone = models.CharField(
        max_length=20,
        verbose_name='Телефон клиента'
    )
    client_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='Email клиента'
    )
    date = models.DateField(
        verbose_name='Дата мероприятия'
    )
    start_time = models.TimeField(
        verbose_name='Время начала'
    )
    end_time = models.TimeField(
        verbose_name='Время окончания'
    )
    guests_count = models.PositiveIntegerField(
        verbose_name='Количество гостей'
    )
    special_requests = models.TextField(
        null=True,
        blank=True,
        verbose_name='Особые пожелания'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус бронирования'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Общая стоимость',
        help_text='Полная стоимость бронирования'
    )
    deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Внесенная предоплата'
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
        return f"Бронирование {self.id} - {self.room.name} на {self.date}"

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['room', 'date']),
            models.Index(fields=['status']),
        ]