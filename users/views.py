from urllib.parse import urlencode
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from django.contrib.auth.models import update_last_login
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from notifications.services import NotificationService

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
logger = logging.getLogger(__name__)


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
        operation_description="[DEPRECATED] Используйте /api/v1/users/profile/me/",
        responses={
            200: ProfileSerializer(),
            401: "Не авторизован"
        },
        tags=['profile', 'deprecated'] 
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


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
            NotificationService.send_welcome_notification(user)
            logger.info(f"Отправлено приветственное уведомление для пользователя: {user.email}")
            
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


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получение профиля текущего пользователя",
        responses={
            200: ProfileSerializer(),
            401: "Не авторизован"
        },
        tags=['profile']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    

    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Обновление профиля текущего пользователя",
        request_body=UserUpdateSerializer,
        responses={
            200: ProfileSerializer(),
            400: "Некорректные данные",
            401: "Не авторизован"
        },
        tags=['profile']
)
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(ProfileSerializer(request.user, context={'request': request}).data)
        
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
            200: openapi.Response(
                description="Успешная загрузка",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'image_url': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Файл не предоставлен",
            401: "Не авторизован"
        },
        tags=['profile']
    )
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
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
            200: openapi.Response(
                description="Успешное удаление",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Не авторизован"
        },
        tags=['profile']
    )
    @action(detail=False, methods=['delete'])
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
        operation_description="Изменение пароля пользователя",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(
                description="Пароль успешно изменен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Некорректные данные",
            401: "Не авторизован"
        },
        tags=['profile']
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data)
        
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


@api_view(['POST'])
@permission_classes([AllowAny])
def google(request):
    form_data = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
        'code': request.data.get('code'),
    }
    form_encode = urlencode(form_data)
    
    get_google_access_token = requests.post(settings.GOOGLE_TOKEN_URI, 
                                            headers={
                                                'Content-Type': 'application/x-www-form-urlencoded'
                                            },
                                            data=form_encode)
    res_access_token = get_google_access_token.json()
    if 'error' in res_access_token:
        return Response(res_access_token, status=get_google_access_token.status_code)
    
    get_user_credentials_from_google = requests.get(settings.GOOGLE_USER_INFO_URI,
                                        headers={
                                            'Authorization': f"Bearer {res_access_token['access_token']}"
                                        })
    res_user_credentials = get_user_credentials_from_google.json()
    if 'error' in get_user_credentials_from_google:
        return Response(res_user_credentials, status=res_user_credentials.status_code)
    print('res_user_credentials', res_user_credentials)
    
    get_user = User.objects.filter(email=res_user_credentials['email'])
    
    if get_user.exists():
        user = User.objects.get(email=res_user_credentials['email'])
        user.is_active = True
        user.google = res_user_credentials['email']
        user.save()
        
        update_last_login(None, user)
        
        create_tokens = RefreshToken.for_user(user)
        return Response({
            'access': str(create_tokens.access_token),
            'refresh': str(create_tokens),
        }, status=status.HTTP_200_OK)
        
    if not get_user.exists():
        new_user = User()
        new_user.username = res_user_credentials['email'].split('@')[0].lower()
        new_user.email = res_user_credentials['email']
        new_user.is_active = True
        new_user.google = res_user_credentials
        new_user.phone_number = '87071362645'
        new_user.save()
        new_user.set_password('123456789')
        
        update_last_login(None, new_user)
        
        create_tokens = RefreshToken.for_user(new_user)
        return Response({
            'access': str(create_tokens.access_token),
            'refresh': str(create_tokens),
        }, status=status.HTTP_200_OK)
        
    return Response({'message': 'Google'}, status=status.HTTP_200_OK)
        
    
    
                                        
    
        