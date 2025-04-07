from django.urls import path
from . import views

urlpatterns = [
    path('dish/<int:dish_id>/', views.get_dish_details, name='dish_details'),
]