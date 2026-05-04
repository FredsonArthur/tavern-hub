from django.urls import path
from . import views

urlpatterns = [
    # --- Rota Principal ---
    path('', views.dashboard, name='dashboard'),

    # --- Rotas do Sistema de Rolagem (API / Entidade 3) ---
    # AJUSTADO: Rotas consistentes para as operações de Create, Read e Delete.
    path('api/rolagem/salvar/', views.salvar_rolagem, name='salvar_rolagem'),
    path('api/rolagem/listar/', views.listar_rolagens, name='listar_rolagens'),
    path('api/rolagem/limpar/', views.limpar_log, name='limpar_log'), 

    # --- Rotas do CRUD de Mesa (Entidade 1) ---
    path('mesas/', views.lista_mesas, name='lista_mesas'),
    path('mesas/nova/', views.criar_mesa, name='criar_mesa'),

    # --- Rotas do CRUD de Personagem (Entidade 2) ---
    # Implementa as rotas para Listagem, Criação, Edição e o novo Soft Delete[cite: 4].
    path('personagens/', views.lista_personagens, name='lista_personagens'),
    path('personagens/novo/', views.criar_personagem, name='criar_personagem'),
    path('personagens/editar/<int:pk>/', views.editar_personagem, name='editar_personagem'),
    path('personagens/excluir/<int:pk>/', views.excluir_personagem, name='excluir_personagem'),
]