from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, Section, Table
from itertools import groupby
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings
from django.utils import timezone
import uuid
from django.db.models import Q


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'opening_time', 'closing_time', 'display_iiko_status', 'id')
    list_filter = ('city',)
    search_fields = ('name', 'city__name', 'iiko_organization_id')
    readonly_fields = ('get_created', 'get_modified')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'city', 'opening_time', 'closing_time')
        }),
        ('Интеграция с iiko', {
            'fields': ('iiko_organization_id', 'external_menu_id', 'price_category_id', 'department_id'),
            'classes': ('collapse',),
            'description': 'Настройки для интеграции с системой iiko'
        }),
    )

    def display_iiko_status(self, obj):
        if obj.iiko_organization_id:
            return format_html('<span style="color:green;">✓</span>')
        return format_html('<span style="color:red;">✕</span>')
    display_iiko_status.short_description = 'iiko'

    def get_created(self, obj):
        return getattr(obj, 'created_at', 'Нет данных')
    get_created.short_description = 'Дата создания'

    def get_modified(self, obj):
        return getattr(obj, 'modified_at', 'Нет данных')
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
    list_display = ['name', 'restaurant', 'get_tables_count']
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