from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.template_views import home_view

api_info = openapi.Info(
    title="Epicure API",
    default_version='v1',
    description="API для системы управления ресторанами Epicure",
    terms_of_service="https://www.epicure.com/terms/",
    contact=openapi.Contact(email="contact@epicure.com"),
    license=openapi.License(name="BSD License"),
)

api_url_patterns = [
    path('api/v1/', include([
        path('cities/', include('cities.urls')),
        path('users/', include('users.urls')),
        path('restaurants/', include('restaurant.urls')),
        path('products/', include('products.urls', namespace='products')),
        path('advertisements/', include('advertisement.urls')),
        path('room/', include('room.urls', namespace='room')),  
    ])),
]

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=api_url_patterns,
    authentication_classes=[], 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/', include([
        path('cities/', include('cities.urls')),
        path('users/', include('users.urls')),
        path('restaurants/', include('restaurant.urls')),
        path('products/', include('products.urls', namespace='products')),
        path('advertisements/', include('advertisement.urls', namespace='advertisement')),
        path('room/', include('room.urls', namespace='room')),  
    ])),
    
    path('api/docs/', include([
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ])),

    path('', home_view, name='home'),
    path('accounts/', include('users.template_urls')),
    path('products/', include('products.urls')),
    path('advertisement/', include('advertisement.urls', namespace='advertisement_templates')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)