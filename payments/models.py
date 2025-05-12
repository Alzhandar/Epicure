
from django.db import models
from users.models import User
from room.models import Reservation


class PaymentType(models.Model):
    TYPE_KIND_CHOICES = (
        ('Cash', 'Наличные'),
        ('Card', 'Карта'),
        ('LoyaltyCard', 'Карта лояльности'),
        ('External', 'Внешний')
    )
    
    payment_type_id = models.CharField(max_length=255, unique=True, db_index=True, verbose_name='ID типа платежа', help_text='payment_type_id')
    name = models.CharField(max_length=255, verbose_name='Название типа платежа')
    description = models.TextField(verbose_name='Описание типа платежа')
    payment_type_kind = models.CharField(max_length=255, verbose_name='Тип платежа в iiko', help_text='payment_type_kind можно получить', choices=TYPE_KIND_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тип платежа'
        verbose_name_plural = 'Типы платежей'
        
        ordering = ['name']
        indexes = [models.Index(fields=['payment_type_id'])]
