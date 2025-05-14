from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _


class LanguageChoice(models.TextChoices):
    RUSSIAN = 'ru', _('Русский')
    KAZAKH = 'kz', _('Қазақша')

class UserManager(BaseUserManager):
    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError(_('Номер телефона должен быть указан'))
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=25,
        unique=True,
        verbose_name='Номер телефона'
    )
    username = models.CharField(
        max_length=50,
        verbose_name='Имя пользователя'
    )
    city = models.ForeignKey(
        'cities.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Город'
    )
    image = models.ImageField(upload_to='users/images/', null=True, blank=True, verbose_name='Аватар')
    email = models.EmailField(null=True, blank=True, verbose_name='Почта')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата и время обновления')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперадмин?')
    is_active = models.BooleanField(default=True, verbose_name='Активен?')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал?')
    language = models.CharField(
        max_length=2,
        default=LanguageChoice.RUSSIAN,
        choices=LanguageChoice.choices,
        verbose_name='Язык'
    )
    google = models.TextField(null=True, blank=True, verbose_name='Google данные')

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    @property
    def full_name(self):
        return self.username