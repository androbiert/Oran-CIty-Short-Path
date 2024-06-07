from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calculate_path', views.calculate_path, name='calculate_path'),
]
