from django.urls import path
from . import views

app_name = 'advertisement'  

urlpatterns = [
    path('banner/<int:banner_id>/click/', views.banner_click, name='banner_click'),
    path('banner/<int:banner_id>/impression/', views.banner_impression, name='banner_impression'),
]