from django.urls import path
from . import views

urlpatterns = [
    # --- Rota Principal ---
    path('', views.dashboard, name='dashboard'),

    # --- Rotas do Sistema de Rolagem (API) ---
    path('salvar-rolagem/', views.salvar_rolagem, name='salvar_rolagem'),
    path('listar-rolagens/', views.listar_rolagens, name='listar_rolagens'),

    # --- Rotas do CRUD de Personagem ---
    path('personagens/', views.lista_personagens, name='lista_personagens'),
    path('personagens/novo/', views.criar_personagem, name='criar_personagem'),
    path('personagens/editar/<int:pk>/', views.editar_personagem, name='editar_personagem'),
    path('personagens/excluir/<int:pk>/', views.excluir_personagem, name='excluir_personagem'),
]