from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label=_('Пароль'))
    password2 = forms.CharField(widget=forms.PasswordInput(), label=_('Подтверждение пароля'))

    class Meta:
        model = User
        fields = ['phone_number', 'username', 'email', 'password', 'password2']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(_('Пользователь с таким номером телефона уже существует.'))
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', _('Пароли не совпадают.'))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = True  
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    phone_number = forms.CharField(label=_('Номер телефона'))
    password = forms.CharField(widget=forms.PasswordInput(), label=_('Пароль'))
    remember_me = forms.BooleanField(required=False, initial=False, label=_('Запомнить меня'))

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')
        
        if phone_number and password:
            self.user = authenticate(phone_number=phone_number, password=password)
            if self.user is None:
                raise forms.ValidationError(_('Неверный номер телефона или пароль.'))
            elif not self.user.is_active:
                raise forms.ValidationError(_('Этот аккаунт не активирован.'))
        return cleaned_data