from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'notification_type', 'recipient_email', 'title', 
        'status', 'created_at', 'read_at'
    ]
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['recipient_email', 'recipient_phone', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at', 'read_at']
    fieldsets = (
        ('Получатель', {
            'fields': ('recipient_email', 'recipient_phone', 'user')
        }),
        ('Контент', {
            'fields': ('title', 'message', 'notification_type')
        }),
        ('Статус', {
            'fields': ('status', 'read_at')
        }),
        ('Связи', {
            'fields': ('reservation',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at')
        }),
    )