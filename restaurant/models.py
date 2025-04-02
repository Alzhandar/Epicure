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
        verbose_name_plural = 'Ресторан'
        indexes = [models.Index(fields=['name'])]


class Section(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Ресторан'
    )
    name = models.CharField(
        'Название секции',
        max_length=255
    )

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    class Meta:
        verbose_name = 'Секция'
        verbose_name_plural = 'Секции'
        indexes = [models.Index(fields=['restaurant', 'name'])]
        unique_together = ['restaurant', 'name']


class Table(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        verbose_name='Уникальный UUID'
    )

    iiko_uuid = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='UUID стола в iiko'
    )

    number = models.IntegerField(
        verbose_name='Номер стола'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='tables',
        verbose_name='Секция',
        null=True,
        blank=True
    )

    qr = models.ImageField(
        upload_to='qr_codes/',
        verbose_name='QR-код',
        blank=True,
        null=True
    )

    call_waiter = models.BooleanField(
        default=False,
        verbose_name='Вызов официанта'
    )
    
    call_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время вызова'
    )
    bill_waiter = models.BooleanField(
        default=False,
        verbose_name='Запрос счёта'
    )
    bill_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время запроса счёта'
    )

    iiko_waiter_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID официанта в iiko'
    )

    class Meta:
        verbose_name = 'Стол и его QR код'
        verbose_name_plural = 'Создание столов и QR кодов'
        ordering = ['number']
        unique_together = (('section', 'number'),)

    def __str__(self):
        sec_name = self.section.name if self.section else "Без секции"
        return f"Стол №{self.number} - {sec_name}"


    def save(self, *args, **kwargs):
        if not self.qr:
            link = f"{settings.BASE_URL}/{self.uuid}/"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(link)
            qr.make(fit=True)
            
            code_img = qr.make_image(fill_color="black", back_color="white")
            
            canvas_size = 450
            canvas = Image.new('RGB', (canvas_size, canvas_size), 'white')
            
            qr_size = code_img.size[0]
            position = ((canvas_size - qr_size) // 2, (canvas_size - qr_size) // 2)
            
            canvas.paste(code_img, position)
            
            buffer = BytesIO()
            canvas.save(buffer, 'PNG')
            file_name = f'table-{self.section.name}-{self.number}-qr.png' if self.section else f'table-{self.number}-qr.png'
            self.qr.save(file_name, File(buffer), save=False)
            buffer.close()
            canvas.close()

        super().save(*args, **kwargs)