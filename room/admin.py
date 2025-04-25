from django.contrib import admin
from django.utils.html import format_html
from .models import Reservation, ReservationMenuItem, ReservationStatus


class ReservationMenuItemInline(admin.TabularInline):
    model = ReservationMenuItem
    extra = 1
    autocomplete_fields = ['menu_item']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'guest_name', 'guest_phone', 'restaurant_name', 'table_number',
        'reservation_date_display', 'time_slot', 'guest_count', 'status_colored', 'created_at'
    ]
    list_filter = ['status', 'reservation_date', 'restaurant']
    search_fields = ['guest_name', 'guest_phone', 'guest_email', 'restaurant__name']
    autocomplete_fields = ['restaurant', 'table']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReservationMenuItemInline]
    date_hierarchy = 'reservation_date'
    fieldsets = (
        ('Информация о бронировании', {
            'fields': ('restaurant', 'table', 'reservation_date', 'start_time', 'end_time', 'guest_count')
        }),
        ('Информация о клиенте', {
            'fields': ('guest_name', 'guest_phone', 'guest_email')
        }),
        ('Статус и комментарии', {
            'fields': ('status', 'special_requests')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def restaurant_name(self, obj):
        return obj.restaurant.name
    restaurant_name.short_description = 'Ресторан'
    restaurant_name.admin_order_field = 'restaurant__name'
    
    def table_number(self, obj):
        return f'№{obj.table.number}'
    table_number.short_description = 'Стол'
    table_number.admin_order_field = 'table__number'
    
    def reservation_date_display(self, obj):
        return obj.reservation_date.strftime('%d.%m.%Y')
    reservation_date_display.short_description = 'Дата'
    reservation_date_display.admin_order_field = 'reservation_date'
    
    def time_slot(self, obj):
        return f'{obj.start_time.strftime("%H:%M")} - {obj.end_time.strftime("%H:%M")}'
    time_slot.short_description = 'Время'
    
    def status_colored(self, obj):
        colors = {
            ReservationStatus.PENDING: '#f4ca16',    
            ReservationStatus.CONFIRMED: '#4caf50',  
            ReservationStatus.CANCELLED: '#f44336',  
            ReservationStatus.COMPLETED: '#2196f3', 
            ReservationStatus.NO_SHOW: '#9c27b0',    
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 5px;">{}</span>',
            colors.get(obj.status, '#777777'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'


@admin.register(ReservationMenuItem)
class ReservationMenuItemAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'menu_item', 'quantity']
    list_filter = ['reservation__status', 'reservation__restaurant']
    search_fields = ['reservation__guest_name', 'menu_item__name_ru']
    autocomplete_fields = ['reservation', 'menu_item']