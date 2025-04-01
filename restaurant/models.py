import uuid
import qrcode
from io import BytesIO
from PIL import Image

from django.db import models
from django.core.files import File
from django.conf import settings
from cities.models import City  

class Restaurant(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название ресторана'
    )

    city = models.ForeignKey(
        City, 
        on_delete=models.CASCADE,
        related_name='restaurants',
        verbose_name='Город'
    )

    iiko_organization_id = models.CharField(
        max_length=255,
        verbose_name='ID организации из iiko Cloud API',
        null=True,
        blank=True
    )
    
    external_menu_id = models.CharField(
        max_length=255,
        verbose_name='Внешний ID меню из iiko Cloud API',
        null=True,
        blank=True
    )

    price_category_id = models.CharField(
        max_length=255,
        verbose_name='ID ценной категории из iiko Cloud API',
        null=True,
        blank=True
    )

    department_id = models.CharField(
        max_length=255,
        verbose_name='ID подразделения из iiko Waiter',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'
        indexes = [models.Index(fields=['name'])]