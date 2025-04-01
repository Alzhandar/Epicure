from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'display_iiko_status', 'id')
    list_filter = ('city',)
    search_fields = ('name', 'city__name', 'iiko_organization_id')
    readonly_fields = ('get_created', 'get_modified')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'city')
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