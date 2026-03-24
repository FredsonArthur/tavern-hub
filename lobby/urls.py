# lobby/urls.py
from django.urls import path
from . import views

# lobby/urls.py
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('salvar-rolagem/', views.salvar_rolagem, name='salvar_rolagem'),
]