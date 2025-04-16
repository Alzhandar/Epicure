from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentType


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_type_id', 'payment_type_kind_display', 'description_preview')
    list_filter = ('payment_type_kind',)
    search_fields = ('name', 'payment_type_id', 'description')
    readonly_fields = ('payment_type_id',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'payment_type_id', 'payment_type_kind')
        }),
        ('Дополнительная информация', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def payment_type_kind_display(self, obj):
        if not obj.payment_type_kind:
            return "-"
            
        kind_colors = {
            'Cash': 'success',
            'Card': 'primary',
            'LoyaltyCard': 'info',
            'External': 'warning'
        }
        color = kind_colors.get(obj.payment_type_kind, 'secondary')
        display_text = dict(PaymentType.TYPE_KIND_CHOICES).get(obj.payment_type_kind, obj.payment_type_kind)
        
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, display_text
        )
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    
    payment_type_kind_display.short_description = 'Тип платежа'
    description_preview.short_description = 'Описание'
    
    class Media:
        css = {
            'all': ('admin/css/admin_styles.css',)
        }