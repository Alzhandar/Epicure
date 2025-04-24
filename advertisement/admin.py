from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.db.models import F, ExpressionWrapper, FloatField
from .models import Banner


class BannerStatusFilter(admin.SimpleListFilter):
    title = 'Статус показа'
    parameter_name = 'display_status'
    
    def lookups(self, request, model_admin):
        return (
            ('current', 'Активные сейчас'),
            ('scheduled', 'Запланированные'),
            ('expired', 'Истекшие'),
            ('inactive', 'Неактивные'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'current':
            return queryset.filter(
                is_active=True,
                start_date__lte=now
            ).filter(
                models.Q(end_date__gte=now) | models.Q(end_date__isnull=True)
            )
            
        if self.value() == 'scheduled':
            return queryset.filter(
                is_active=True,
                start_date__gt=now
            )
            
        if self.value() == 'expired':
            return queryset.filter(
                end_date__lt=now
            )
            
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'status_badge', 'priority', 'display_period', 
                   'impressions', 'clicks', 'ctr_display')
    list_filter = (BannerStatusFilter, 'position', 'color_scheme', 'is_active')
    search_fields = ('title', 'subtitle', 'content')
    readonly_fields = ('impressions', 'clicks', 'ctr_display', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'subtitle', 'content', 'image')
        }),
        ('Настройки отображения', {
            'fields': ('position', 'color_scheme', 'priority', 'is_active')
        }),
        ('Период показа', {
            'fields': ('start_date', 'end_date')
        }),
        ('Действие', {
            'fields': ('url', 'button_text'),
            'description': 'Настройки для кнопки или ссылки баннера'
        }),
        ('Статистика', {
            'fields': ('impressions', 'clicks', 'ctr_display'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        now = timezone.now()
        
        if not obj.is_active:
            return format_html(
                '<span class="badge badge-secondary">Неактивен</span>'
            )
            
        if obj.start_date > now:
            days_until = (obj.start_date - now).days
            return format_html(
                '<span class="badge badge-info">Запланирован (через {} дн.)</span>',
                days_until
            )
            
        if obj.end_date and obj.end_date < now:
            return format_html(
                '<span class="badge badge-danger">Истек</span>'
            )
            
        if obj.end_date:
            days_left = (obj.end_date - now).days
            return format_html(
                '<span class="badge badge-success">Активен (еще {} дн.)</span>',
                days_left
            )
        else:
            return format_html(
                '<span class="badge badge-success">Активен (бессрочно)</span>'
            )
    
    def display_period(self, obj):
        start = obj.start_date.strftime('%d.%m.%Y')
        if obj.end_date:
            end = obj.end_date.strftime('%d.%m.%Y')
            return f"{start} — {end}"
        return f"С {start} (бессрочно)"
    
    def ctr_display(self, obj):
        ctr = obj.ctr
        
        if obj.impressions == 0:
            return "Нет данных"
            
        if ctr > 5:
            color = "green"
        elif ctr > 2:
            color = "#f29c13"  
        else:
            color = "red"
            
        return format_html('<span style="color: {}; font-weight: bold">{:.2f}%</span>', color, ctr)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            ctr_value=ExpressionWrapper(
                F('clicks') * 100.0 / F('impressions'),
                output_field=FloatField()
            )
        )
        return qs
    
    def get_ordering(self, request):
        return ['-priority', '-start_date']
        
    status_badge.short_description = 'Статус'
    display_period.short_description = 'Период показа'
    ctr_display.short_description = 'CTR'
    
    class Media:
        css = {
            'all': ('admin/css/admin_banners.css',)
        }
        js = ('admin/js/banner_admin.js',)