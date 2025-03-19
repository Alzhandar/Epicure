from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
                schema=ProfileSerializer()
            ),
            401: "Не авторизован"
        }
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Изменение пароля пользователя",
        request_body=PasswordChangeSerializer,
        responses={
            200: "Пароль успешно изменен",
            400: "Некорректные данные",
            404: "Пользователь не найден"
        }
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
            200: "Пользователь успешно активирован",
            404: "Пользователь не найден"
        }
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
            200: "Пользователь успешно деактивирован",
            404: "Пользователь не найден"
        }
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


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        responses={
            201: "Пользователь успешно создан",
            400: "Некорректные данные"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"message": "Пользователь успешно зарегистрирован", "user": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)