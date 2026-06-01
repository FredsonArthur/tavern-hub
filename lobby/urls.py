from django.urls import path
from django.contrib.auth import views as auth_views  # Importa as views de autenticação nativas
from . import views

urlpatterns = [
    # --- Rota Principal (Força o redirecionamento para o login caso não esteja autenticado) ---
    path('', views.dashboard, name='dashboard'),

    # --- AUTENTICAÇÃO: Criação de Novas Contas ---
    path('registro/', views.registro, name='registro'),

    # --- REQUISITO: PAINEL DE ESTATÍSTICAS (Aggregation) ---
    path('estatisticas/', views.painel_estatisticas, name='painel_estatisticas'),

    # --- REQUISITO: SISTEMA DE ROLLBACK (Controle de Versão) ---
    path('rolagem/rollback/<int:pk>/', views.rollback_rolagem, name='rollback_rolagem'),

    # --- Rotas do Sistema de Rolagem (API / Entidade 3) ---
    path('api/rolagem/salvar/', views.salvar_rolagem, name='salvar_rolagem'),
    path('api/rolagem/listar/', views.listar_rolagens, name='listar_rolagens'),
    path('api/rolagem/limpar/', views.limpar_log, name='limpar_log'), 

    # --- Rotas do CRUD de Mesa (Entidade 1 - Protegida) ---
    path('mesas/', views.lista_mesas, name='lista_mesas'),
    path('mesas/nova/', views.criar_mesa, name='criar_mesa'),

    # --- Rotas do CRUD de Personagem (Entidade 2 - Com Soft Delete) ---
    path('personagens/', views.lista_personagens, name='lista_personagens'),
    path('personagens/novo/', views.criar_personagem, name='criar_personagem'),
    path('personagens/editar/<int:pk>/', views.editar_personagem, name='editar_personagem'),
    path('personagens/excluir/<int:pk>/', views.excluir_personagem, name='excluir_personagem'),

    # --- NOVO REQUISITO: GESTÃO DE INVENTÁRIO & ITENS (Many-to-Many) ---
    # Rota para gerenciar os itens de um personagem específico
    path('personagem/<int:pk>/inventario/', views.gerenciar_inventario, name='gerenciar_inventario'),
    
    # Rotas para o CRUD global de Itens (Biblioteca de Itens)
    path('itens/', views.lista_itens, name='lista_itens'),
    path('itens/novo/', views.criar_item, name='criar_item'),
]