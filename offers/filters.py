import django_filters
from .models import Offer, OfferReservation


class OfferFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="new_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="new_price", lookup_expr='lte')
    city = django_filters.NumberFilter(field_name="restaurant__city")
    
    class Meta:
        model = Offer
        fields = {
            'restaurant': ['exact'],
            'offer_type': ['exact'],
            'people_count': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
        }


class OfferReservationFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name="date", lookup_expr='lte')
    
    class Meta:
        model = OfferReservation
        fields = {
            'offer': ['exact'],
            'user': ['exact'],
            'table': ['exact'],
            'status': ['exact'],
        }