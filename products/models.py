from django.db import models
from restaurant.models import Restaurant


class MenuType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Тип меню'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип меню'
        verbose_name_plural = 'Типы меню'


class Menu(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menus',
        verbose_name='Ресторан'
    )
    menu_type = models.ForeignKey(
        MenuType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menus',
        verbose_name='Тип меню'
    )
    name_ru = models.CharField(
        max_length=255,
        verbose_name='Название блюда (Русский)'
    )
    name_kz = models.CharField(
        max_length=255,
        verbose_name='Название блюда (Казахский)'
    )
    image = models.ImageField(
        upload_to='menus/images/',
        null=True,
        blank=True,
        verbose_name='Изображение блюда'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание блюда'
    )
    calories = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Калории (ккал)',
        help_text='Укажите калорийность блюда в килокалориях'
    )
    proteins = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Белки (г)',
        help_text='Укажите количество белков в граммах'
    )
    fats = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Жиры (г)',
        help_text='Укажите количество жиров в граммах'
    )
    carbohydrates = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Углеводы (г)',
        help_text='Укажите количество углеводов в граммах'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        help_text='Укажите цену блюда в тенге'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступно?',
        help_text='Отметьте, если блюдо доступно для заказа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время обновления'
    )

    def __str__(self):
        return f"{self.name_ru} ({self.restaurant.name})"

    def is_healthy(self):
        return self.calories is not None and self.calories < 500

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        indexes = [
            models.Index(fields=['name_ru', 'restaurant']),
            models.Index(fields=['is_available']),
        ]
