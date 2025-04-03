from django.contrib import admin
from django.utils.html import format_html
from .models import RoomType, BookingType, Room, RoomImage, Package, PackageMenu, Booking


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(BookingType)
class BookingTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ('image', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="100" />', obj.image.url)
        return "Нет изображения"
    
    image_preview.short_description = 'Превью изображения'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant', 'section', 'room_type', 'capacity', 
                   'price_per_hour', 'is_active')
    list_filter = ('restaurant', 'room_type', 'is_active')
    search_fields = ('name', 'restaurant__name', 'section__name')
    inlines = [RoomImageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'restaurant', 'section', 'room_type')
        }),
        ('Характеристики комнаты', {
            'fields': ('capacity', 'area', 'price_per_hour', 'description', 'features', 'is_active')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class PackageMenuInline(admin.TabularInline):
    model = PackageMenu
    extra = 1
    fields = ('menu_item', 'quantity', 'notes')
    autocomplete_fields = ('menu_item',)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'room', 'booking_type', 'price', 'min_guests', 
                   'max_guests', 'is_active')
    list_filter = ('room__restaurant', 'booking_type', 'is_active')
    search_fields = ('name', 'room__name', 'room__restaurant__name')
    inlines = [PackageMenuInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'room', 'booking_type')
        }),
        ('Информация о пакете', {
            'fields': ('description', 'price', 'min_guests', 'max_guests', 'is_active')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('room',)


@admin.register(PackageMenu)
class PackageMenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'package', 'menu_item', 'quantity')
    list_filter = ('package__room__restaurant', 'package')
    search_fields = ('package__name', 'menu_item__name_ru')
    autocomplete_fields = ('package', 'menu_item')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'booking_type', 'client_name', 'client_phone',
                   'date', 'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('room__restaurant', 'booking_type', 'date', 'status')
    search_fields = ('client_name', 'client_phone', 'room__name', 'room__restaurant__name')
    fieldsets = (
        (None, {
            'fields': ('room', 'package', 'booking_type'),
        }),
        ('Информация о клиенте', {
            'fields': ('client_name', 'client_phone', 'client_email'),
        }),
        ('Детали бронирования', {
            'fields': ('date', 'start_time', 'end_time', 'guests_count', 'special_requests'),
        }),
        ('Статус и оплата', {
            'fields': ('status', 'total_price', 'deposit'),
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('room', 'package')
    
    def save_model(self, request, obj, form, change):
        if not obj.id:
            if obj.package:
                obj.total_price = obj.package.price
            else:
                from datetime import datetime
                time_diff = (
                    datetime.combine(obj.date, obj.end_time) - 
                    datetime.combine(obj.date, obj.start_time)
                ).seconds / 3600
                obj.total_price = obj.room.price_per_hour * time_diff
        
        super().save_model(request, obj, form, change)