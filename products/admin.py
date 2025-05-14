from django.contrib import admin
from .models import Menu, MenuType


@admin.register(MenuType)
class MenuTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_ru', 'name_kz')
    search_fields = ('name_ru', 'name_kz')
    ordering = ('name_ru',)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name_ru', 'name_kz', 'restaurant', 'menu_type',
        'price', 'calories', 'is_available', 'is_popular', 'created_at', 'is_healthy_display'
    )
    list_filter = (
        'restaurant', 'menu_type', 'is_available', 'is_popular', 'created_at'
    )
    search_fields = ('name_ru', 'name_kz', 'restaurant__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': (
                'restaurant', 'menu_type',
                'name_ru', 'name_kz',
                'image', 'description_ru', 'description_kz'
            )
        }),
        ('Дополнительная информация', {
            'fields': (
                'calories', 'proteins', 'fats', 'carbohydrates',
                'price', 'is_available', 'is_popular'
            )
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def is_healthy_display(self, obj):
        return obj.is_healthy()
    is_healthy_display.short_description = 'Низкокалорийное?'
    is_healthy_display.boolean = True
