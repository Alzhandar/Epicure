from django.urls import path
from . import template_views

urlpatterns = [
    path('register/', template_views.register_view, name='register'),
    path('login/', template_views.login_view, name='login'),
    path('logout/', template_views.logout_view, name='logout'),
    path('profile/', template_views.profile_view, name='profile'),
    path('set-city/', template_views.set_city, name='set_city'),
]