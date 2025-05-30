from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, Section, Table, Review
from itertools import groupby
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings
from django.utils import timezone
import uuid
from django.db.models import Q, Avg


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'opening_time', 'closing_time', 'display_rating', 'display_iiko_status', 'id', 'photo')
    list_filter = ('city',)
    search_fields = ('name', 'city__name', 'iiko_organization_id')
    readonly_fields = ('get_created', 'get_modified', 'rating', 'reviews_count')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'city', 'opening_time', 'closing_time', 'photo')
        }),
        ('Описания', {
            'fields': ('description_ru', 'description_kz'),
            'classes': ('wide',),
            'description': 'Описания ресторана на разных языках'
        }),
        ('Отзывы', {
            'fields': ('rating', 'reviews_count'),
            'description': 'Статистика отзывов (только для чтения)'
        }),
        ('Интеграция c iiko', {
            'fields': ('iiko_organization_id', 'external_menu_id', 'price_category_id', 'department_id'),
            'classes': ('collapse',),
            'description': 'Настройки для интеграции c системой iiko'
        }),
    )

    def display_iiko_status(self, obj):
        if obj.iiko_organization_id:
            return format_html('<span style="color:green;">✓</span>')
        return format_html('<span style="color:red;">✕</span>')
    display_iiko_status.short_description = 'iiko'

    def display_rating(self, obj):
        if hasattr(obj, 'rating') and obj.rating > 0:
            stars = '★' * int(round(obj.rating))
            return format_html('<span style="color:gold;">{}</span> ({}/5, {} отзывов)', 
                            stars, round(obj.rating, 1), obj.reviews_count)
        return "Нет отзывов"
    display_rating.short_description = 'Рейтинг'

    def get_created(self, obj):
        return getattr(obj, 'created_at', 'Нет данных')
    get_created.short_description = 'Дата создания'

    def get_modified(self, obj):
        return getattr(obj, 'updated_at', 'Нет данных')
    get_modified.short_description = 'Последнее изменение'

    actions = ['mark_no_iiko']
    
    def mark_no_iiko(self, request, queryset):
        queryset.update(iiko_organization_id=None, external_menu_id=None, price_category_id=None, department_id=None)
        self.message_user(request, f"Очищены данные интеграции iiko для {queryset.count()} ресторанов.")
    mark_no_iiko.short_description = "Очистить данные интеграции с iiko"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('city')


class TableInline(admin.TabularInline):
    model = Table
    extra = 1
    show_change_link = True
    readonly_fields = ['qr_preview']
    fields = ['number', 'qr_preview']

    def qr_preview(self, obj):
        if obj and obj.qr:
            return format_html('<img src="{}" width="70" height="70"/>', obj.qr.url)
        return "QR код будет создан после сохранения"
    qr_preview.short_description = 'Предпросмотр'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'get_tables_count', 'photo']
    list_filter = ['restaurant']
    search_fields = ['name', 'restaurant__name']
    autocomplete_fields = ['restaurant']
    inlines = [TableInline]

    def get_tables_count(self, obj):
        return obj.tables.count()
    get_tables_count.short_description = "Столы"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('restaurant')
    

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = [
        'table_number',
        'section_info',
        'qr_preview',
        'download_qr',
        'status_display',
        'call_time',
        'bill_time',
        'iiko_waiter_id'
    ]
    
    list_filter = [
        'section__restaurant',
        'section',
        'call_waiter',
        'bill_waiter'
    ]
    
    search_fields = [
        'number',
        'section__name',
        'section__restaurant__name',
        'iiko_waiter_id'
    ]
    
    readonly_fields = ['qr_preview', 'download_qr']
    autocomplete_fields = ['section']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'uuid',
                'iiko_uuid',
                'number',
                'section',
            )
        }),
        ('Интеграция с iiko', {
            'fields': (
                'iiko_waiter_id',
            ),
            'classes': ('collapse',),
            'description': 'Идентификаторы с системой iiko'
        }),
        ('QR код', {
            'fields': ('qr_preview', 'download_qr'),
        }),
        ('Статус обслуживания', {
            'fields': (
                ('call_waiter', 'call_time'),
                ('bill_waiter', 'bill_time')
            ),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if obj:  
            ro_fields += ['number', 'section']
            ro_fields.append('uuid')
        return ro_fields
    
    def table_number(self, obj):
        return f"Стол №{obj.number}"
    table_number.short_description = "Номер"

    def section_info(self, obj):
        if obj.section:
            return f"{obj.section.restaurant.name} - {obj.section.name}"
        return "Не назначено"
    section_info.short_description = "Расположение"

    def qr_preview(self, obj):
        if obj.qr:
            return format_html(
                '<div style="text-align: center;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" width="100" height="100" style="cursor: pointer;"/>'
                '</a><br>'
                '<a href="{}" target="_blank" '
                'style="display: inline-block; padding: 5px 15px; margin-top: 5px; '
                'background-color: #417690; color: white; text-decoration: none; '
                'border-radius: 4px; font-size: 12px;">'
                'Перейти</a>'
                '</div>',
                f"{settings.BASE_URL}/{obj.uuid}/", 
                obj.qr.url,  
                f"{settings.BASE_URL}/{obj.uuid}/"   
            )
        return "QR код отсутствует"
    qr_preview.short_description = 'QR код'

    def download_qr(self, obj):
        if obj.qr:
            return format_html('<a href="{}" download>Скачать</a>', obj.qr.url)
        return "QR код отсутствует"
    download_qr.short_description = "Скачать QR"

    def status_display(self, obj):
        status = []
        if obj.call_waiter:
            if obj.call_time:
                status.append(f"Вызов официанта ({obj.call_time.strftime('%H:%M')})")
            else:
                status.append("Вызов официанта")
        if obj.bill_waiter:
            if obj.bill_time:
                status.append(f"Запрос счёта ({obj.bill_time.strftime('%H:%M')})")
            else:
                status.append("Запрос счёта")
        if status:
            return format_html("<br>".join(status))
        return "Нет активных запросов"
    status_display.short_description = "Статус стола"

    def save_model(self, request, obj, form, change):
        try:
            if not change:
                existing_table = Table.objects.filter(
                    section=obj.section,
                    number=obj.number
                ).exists()
                
                if existing_table:
                    raise ValidationError(
                        f'Стол №{obj.number} уже существует в секции "{obj.section.name}"'
                    )
            if not obj.uuid:
                obj.uuid = uuid.uuid4()
                
            if obj.call_waiter and not obj.call_time:
                obj.call_time = timezone.now()
            if obj.bill_waiter and not obj.bill_time:
                obj.bill_time = timezone.now()
                
            super().save_model(request, obj, form, change)
            
        except IntegrityError as e:
            raise ValidationError(
                f'Ошибка при создании стола №{obj.number}: {str(e)}'
            )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('section', 'section__restaurant')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'restaurant_name', 'user_info', 'rating_stars', 'short_comment', 'created_at']
    list_filter = ['rating', 'restaurant', 'created_at']
    search_fields = ['comment', 'user__phone_number', 'user__username', 'restaurant__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'restaurant']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('restaurant', 'user', 'rating', 'comment')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def restaurant_name(self, obj):
        return obj.restaurant.name
    restaurant_name.short_description = 'Ресторан'
    
    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.phone_number})"
        return "Анонимно"
    user_info.short_description = 'Пользователь'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:gold;">{}</span>', stars)
    rating_stars.short_description = 'Оценка'
    
    def short_comment(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return "Нет комментария"
    short_comment.short_description = 'Комментарий'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('restaurant', 'user')
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False