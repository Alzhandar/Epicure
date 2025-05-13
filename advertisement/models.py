from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import os


def banner_image_path(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    current_date = timezone.now()
    return 'banners/{year}/{month}/{slug}{ext}'.format(
        year=current_date.strftime('%Y'),
        month=current_date.strftime('%m'),
        slug=slugify(instance.title),
        ext=filename_ext.lower(),
    )


class Banner(models.Model):
    POSITION_CHOICES = (
        ('hero', 'Основная область (Hero)'),
        ('above_restaurants', 'Над списком ресторанов'),
        ('above_dishes', 'Над списком блюд'),
    )
    
    COLOR_SCHEME_CHOICES = (
        ('light', 'Светлая (темный текст)'),
        ('dark', 'Темная (светлый текст)'),
        ('primary', 'Основной цвет'),
        ('accent', 'Акцентный цвет'),
    )
    
    title_ru = models.CharField(max_length=200, verbose_name='Заголовок')
    title_kz = models.CharField(max_length=200, null=True, blank=True, verbose_name='Заголовок (Казакша епт)')
    subtitle_ru = models.CharField(max_length=300, blank=True, null=True, verbose_name='Подзаголовок')
    subtitle_kz = models.CharField(max_length=300, null=True, blank=True, verbose_name='ПодЗаголовок (Казахский)')
    content_ru = models.TextField(blank=True, null=True, verbose_name='Содержание')
    content_kz = models.TextField(null=True, blank=True, verbose_name='Содержание (Казахский)')
    image = models.ImageField(upload_to=banner_image_path, verbose_name='Изображение', 
                             help_text='размер: 1200x400 пикселей')
    
    url = models.URLField(verbose_name='URL ссылки', blank=True, null=True, 
                         help_text='Внешняя ссылка или путь внутри сайта')
    button_text_ru = models.CharField(max_length=50, blank=True, null=True, verbose_name='Текст кнопки',
                                 help_text='если кнопка не нужна')
    button_text_kz = models.CharField(max_length=50, null=True, blank=True, verbose_name='Текст кнопки (Казахский)')
    
    start_date = models.DateTimeField(default=timezone.now, verbose_name='Дата начала показа')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания показа',
                                  help_text='бессрочного показа')
    
    priority = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
                                 verbose_name='Приоритет', 
                                 help_text='От 1 (низкий) до 10 (высокий)')
    
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='hero', 
                              verbose_name='Позиция на странице')
    
    color_scheme = models.CharField(max_length=10, choices=COLOR_SCHEME_CHOICES, default='light',
                                  verbose_name='Цветовая схема')
    
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    clicks = models.PositiveIntegerField(default=0, verbose_name='Количество кликов', editable=False)
    impressions = models.PositiveIntegerField(default=0, verbose_name='Количество показов', editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ['-priority', '-start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date', 'is_active']),
            models.Index(fields=['position']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return self.title
        
    def is_current(self):
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.start_date and now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True
    
    def record_impression(self):
        self.impressions += 1
        self.save(update_fields=['impressions'])
        
    def record_click(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])
    
    @property
    def ctr(self):
        if self.impressions == 0:
            return 0
        return round((self.clicks / self.impressions) * 100, 2)
