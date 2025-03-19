import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter')
    name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    city = django_filters.NumberFilter(field_name='city__id')
    city_name = django_filters.CharFilter(field_name='city__name', lookup_expr='icontains')
    language = django_filters.ChoiceFilter(choices=[('ru', 'Русский'), ('en', 'Английский')])
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['name', 'last_name', 'phone_number', 'email', 'is_active', 
                 'city', 'city_name', 'language']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(phone_number__icontains=value) |
            Q(email__icontains=value)
        )