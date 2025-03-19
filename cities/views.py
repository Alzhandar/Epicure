from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Max

from .models import City
from .permissions import IsAdminOrReadOnly
from .serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('position', 'name')
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'position']
    ordering = ['position', 'name']
    
    def perform_create(self, serializer):
        if not serializer.validated_data.get('position'):
            max_position = City.objects.aggregate(Max('position'))['position__max']
            serializer.save(position=(max_position or 0) + 1)
        else:
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"error": "Ожидается список объектов"}, status=status.HTTP_400_BAD_REQUEST)
            
        for item in items:
            try:
                city = City.objects.get(id=item['id'])
                city.position = item['position']
                city.save(update_fields=['position'])
            except (City.DoesNotExist, KeyError):
                pass
                
        return Response(status=status.HTTP_200_OK)


