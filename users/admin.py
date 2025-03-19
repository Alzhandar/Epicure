from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django import forms

from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'last_name', 'email', 'city')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Пароли не совпадают'))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    
    list_display = ('phone_number', 'name', 'last_name', 'email', 'display_city', 
                    'language', 'is_active', 'is_staff', 'display_photo')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'city', 'language', 'created_at')
    search_fields = ('phone_number', 'name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('phone_number', 'password')
        }),
        (_('Персональная информация'), {
            'fields': ('name', 'last_name', 'email', 'city', 'image', 'language')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'last_name', 'email', 'city', 'password1', 'password2'),
        }),
    )

    def display_city(self, obj):
        if obj.city:
            return obj.city.name
        return '-'
    display_city.short_description = _('Город')

    def display_photo(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', 
                              obj.image.url)
        return format_html('<span style="color: gray;">нет фото</span>')
    display_photo.short_description = _('Фото')
    
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} пользователей')
    activate_users.short_description = _("Активировать выбранных пользователей")
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} пользователей')
    deactivate_users.short_description = _("Деактивировать выбранных пользователей")