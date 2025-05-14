from rest_framework import viewsets
from .models import Restaurant, Section, Table, Review
from rest_framework.decorators import action
from .serializers import RestaurantSerializer, SectionSerializer, TableSerializer, ReviewSerializer
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city']
    search_fields = ['name', 'description_ru', 'description_kz']
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        restaurant = self.get_object()
        reviews = Review.objects.filter(restaurant=restaurant)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['restaurant', 'user', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    


from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

@api_view(['POST'])
@parser_classes([MultiPartParser])
def test_spaces_upload(request):
    if 'file' not in request.FILES:
        return Response({'error': 'Файл не найден'}, status=400)
        
    file = request.FILES['file']
    filename = default_storage.save(f'test_uploads/{file.name}', file)
    file_url = default_storage.url(filename)
    
    return Response({
        'success': True,
        'filename': filename,
        'url': file_url,
        'storage_type': 'Digital Ocean Spaces' 
    })