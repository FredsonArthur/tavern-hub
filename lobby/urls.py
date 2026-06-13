from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # --- Rota Principal (Força o redirecionamento para o login caso não esteja autenticado) ---
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),  # ← Adicione esta linha
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # ← Adicione

    # --- AUTENTICAÇÃO: Criação de Novas Contas ---
    path('registro/', views.registro, name='registro'),

    # --- REQUISITO: PAINEL DE ESTATÍSTICAS (Aggregation) ---
    path('estatisticas/', views.painel_estatisticas, name='painel_estatisticas'),

    # --- REQUISITO: SISTEMA DE ROLLBACK (Controle de Versão) ---
    path('rolagem/rollback/<int:pk>/', views.rollback_rolagem, name='rollback_rolagem'),

    # Ficha do personagem
    path('personagem/<int:pk>/', views.ficha_personagem, name='ficha_personagem'),

    # APIs de cura/dano
    path('api/personagem/<int:pk>/curar/', views.api_curar_personagem, name='api_curar_personagem'),
    path('api/personagem/<int:pk>/dano/', views.api_dano_personagem, name='api_dano_personagem'),

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