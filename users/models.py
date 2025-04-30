from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _


class LanguageChoice(models.TextChoices):
    RUSSIAN = 'ru', _('Русский')
    KAZAKH = 'kz', _('Қазақша')

class UserManager(BaseUserManager):
    def _create_user(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(password, **extra_fields)

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=25,
        unique=True,
        verbose_name='Номер телефона'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Фамилия'
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
    is_active = models.BooleanField(default=False, verbose_name='Активен?')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал?')
    language = models.CharField(
        max_length=2,
        default=LanguageChoice.RUSSIAN,
        choices=LanguageChoice.choices,
        verbose_name='Язык'
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    @property
    def full_name(self):
        return f'{self.last_name} {self.name}' if self.last_name else self.name