"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

api_info = openapi.Info(
    title="Epicure API",
    default_version='v1',
    description="Epicure API Documentation",
    terms_of_service="https://www.epicure.com/terms/",
    contact=openapi.Contact(email="contact@epicure.com"),
    license=openapi.License(name="BSD License"),
)

api_url_patterns = [
    path('api/v1/', include('cities.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('restaurant.urls')),
]

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=api_url_patterns,  
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/', include('cities.urls')),
    path('api/v1/', include('users.urls')),
    
    path('', RedirectView.as_view(url='/api/swagger/', permanent=False)),
    
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', 
        schema_view.without_ui(cache_timeout=0), 
        name='schema-json'),
    path('api/swagger/', 
        schema_view.with_ui('swagger', cache_timeout=0), 
        name='schema-swagger-ui'),
    path('api/redoc/', 
        schema_view.with_ui('redoc', cache_timeout=0), 
        name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)