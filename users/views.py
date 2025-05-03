from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    UserDetailSerializer,
    PasswordChangeSerializer,
    ProfileSerializer
)
from .permissions import IsUpdatingOwnAccount
from .filters import UserFilter
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['name', 'last_name', 'phone_number', 'email']
    ordering_fields = ['name', 'created_at', 'city']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        elif self.action == 'me':
            return ProfileSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsUpdatingOwnAccount]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        operation_description="Получение профиля текущего пользователя",
        responses={
            200: openapi.Response(
                description="Успешное получение профиля",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    title="Профиль"
                )
            ),
            401: openapi.Response(description="Не авторизован")
        },
        tags=['users'] 
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Изменение пароля пользователя",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(description="Пароль успешно изменен"),
            400: openapi.Response(description="Некорректные данные"),
            404: openapi.Response(description="Пользователь не найден")
        },
        tags=['users']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsUpdatingOwnAccount])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data.get('current_password')):
                return Response(
                    {'current_password': ['Неверный текущий пароль']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            
            return Response({'status': 'Пароль успешно изменен'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Активация пользователя",
        responses={
            200: openapi.Response(description="Пользователь успешно активирован"),
            403: openapi.Response(description="Недостаточно прав"),
            404: openapi.Response(description="Пользователь не найден")
        },
        tags=['users']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        user = self.get_object()
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {"detail": "У вас недостаточно прав для выполнения этого действия."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = True
        user.save()
        
        return Response({"status": "Пользователь успешно активирован"})
    
    @swagger_auto_schema(
        operation_description="Деактивация пользователя",
        responses={
            200: openapi.Response(description="Пользователь успешно деактивирован"),
            403: openapi.Response(description="Недостаточно прав"),
            404: openapi.Response(description="Пользователь не найден")
        },
        tags=['users']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {"detail": "У вас недостаточно прав для выполнения этого действия."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = False
        user.save()
        
        return Response({"status": "Пользователь успешно деактивирован"})

    @swagger_auto_schema(
        methods=['put', 'patch'], 
        operation_description="Обновление профиля текущего пользователя",
        request_body=UserUpdateSerializer,
        responses={
            200: openapi.Response(description="Профиль успешно обновлен"),
            400: openapi.Response(description="Некорректные данные"),
            401: openapi.Response(description="Не авторизован")
        },
        tags=['profile']
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            profile_serializer = ProfileSerializer(user)
            return Response(profile_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Загрузка фотографии профиля",
        manual_parameters=[
            openapi.Parameter(
                name='image',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Фотография профиля'
            )
        ],
        responses={
            200: openapi.Response(description="Фотография успешно загружена"),
            400: openapi.Response(description="Некорректный файл"),
            401: openapi.Response(description="Не авторизован")
        },
        tags=['profile']
    )
    @action(detail=False, methods=['post'], url_path='upload-photo', parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request):
        user = request.user
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Отсутствует файл изображения'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.image = request.FILES['image']
        user.save()
        
        return Response({
            'status': 'success',
            'message': 'Фотография профиля успешно обновлена',
            'image_url': request.build_absolute_uri(user.image.url) if user.image else None
        })
    
    @swagger_auto_schema(
        operation_description="Удаление фотографии профиля",
        responses={
            200: openapi.Response(description="Фотография успешно удалена"),
            401: openapi.Response(description="Не авторизован")
        },
        tags=['profile']
    )
    @action(detail=False, methods=['delete'], url_path='delete-photo')
    def delete_photo(self, request):
        user = request.user
        
        if user.image:
            user.image.delete(save=True)
            user.image = None
            user.save()
            
        return Response({
            'status': 'success',
            'message': 'Фотография профиля успешно удалена'
        })
    @swagger_auto_schema(
        operation_description="Получение профиля текущего пользователя",
        responses={
            200: openapi.Response(
                description="Успешное получение профиля",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    title="Профиль"
                )
            ),
            401: openapi.Response(description="Не авторизован")
        },
        tags=['profile'] 
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


import logging
logger = logging.getLogger(__name__)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info(f"Получен запрос на регистрацию: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Ошибки валидации: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = self.perform_create(serializer)
            logger.info(f"Пользователь успешно создан: {user.phone_number}")
            return Response(
                {"status": "success", "message": "User registered successfully"}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        return user
    

