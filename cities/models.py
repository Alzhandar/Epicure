from django.db import models


class City(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название', unique=True)
    name_ru = models.CharField(max_length=255, verbose_name='Название (RU)', blank=True, null=True)
    name_kz = models.CharField(max_length=255, verbose_name='Название (KZ)', blank=True, null=True)
    position = models.PositiveIntegerField(null=True, verbose_name='Позиция')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'