from django.urls import path
from . import views

urlpatterns = [
    # --- Rota Principal ---
    path('', views.dashboard, name='dashboard'),

    # --- Rotas do Sistema de Rolagem (API) ---
    path('salvar-rolagem/', views.salvar_rolagem, name='salvar_rolagem'),
    path('listar-rolagens/', views.listar_rolagens, name='listar_rolagens'),

    # --- Rotas do CRUD de Mesa (Entidade 1) ---
    path('mesas/', views.lista_mesas, name='lista_mesas'),
    path('mesas/nova/', views.criar_mesa, name='criar_mesa'),

    # --- Rotas do CRUD de Personagem (Entidade 2) ---
    path('personagens/', views.lista_personagens, name='lista_personagens'),
    path('personagens/novo/', views.criar_personagem, name='criar_personagem'),
    path('personagens/editar/<int:pk>/', views.editar_personagem, name='editar_personagem'),
    path('personagens/excluir/<int:pk>/', views.excluir_personagem, name='excluir_personagem'),
]