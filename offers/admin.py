from django.contrib import admin
from .models import Offer, OfferItem, OfferReservation


class OfferItemInline(admin.TabularInline):
    model = OfferItem
    extra = 4


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'restaurant', 'offer_type', 'new_price', 'badge', 'people_count', 'is_active']
    list_filter = ['offer_type', 'restaurant', 'is_active', 'per_person']
    search_fields = ['title_ru', 'restaurant__name']
    inlines = [OfferItemInline]


@admin.register(OfferReservation)
class OfferReservationAdmin(admin.ModelAdmin):
    list_display = ['offer', 'user', 'date', 'time', 'guest_count', 'status']
    list_filter = ['status', 'date', 'offer__restaurant']
    search_fields = ['user__username', 'user__phone_number', 'offer__title_ru']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['confirm_reservations', 'cancel_reservations']
    
    def confirm_reservations(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"{updated} бронирований подтверждено.")
    confirm_reservations.short_description = "Подтвердить выбранные бронирования"
    
    def cancel_reservations(self, request, queryset):
        updated = queryset.exclude(status='cancelled').update(status='cancelled')
        self.message_user(request, f"{updated} бронирований отменено.")
    cancel_reservations.short_description = "Отменить выбранные бронирования"