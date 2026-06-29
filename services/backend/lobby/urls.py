from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # --- Rota Principal ---
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # --- AUTENTICAÇÃO ---
    path('registro/', views.registro, name='registro'),

    # --- ESTATÍSTICAS ---
    path('estatisticas/', views.painel_estatisticas, name='painel_estatisticas'),

    # --- ROLLBACK ---
    path('rolagem/rollback/<int:pk>/', views.rollback_rolagem, name='rollback_rolagem'),

    # --- FICHA DO PERSONAGEM ---
    path('personagem/<int:pk>/', views.ficha_personagem, name='ficha_personagem'),

    # --- APIs DE CURA/DANO ---
    path('api/personagem/<int:pk>/curar/', views.api_curar_personagem, name='api_curar_personagem'),
    path('api/personagem/<int:pk>/dano/', views.api_dano_personagem, name='api_dano_personagem'),

    # --- API DE ROLAGENS ---
    path('api/rolagem/salvar/', views.salvar_rolagem, name='salvar_rolagem'),
    path('api/rolagem/listar/', views.listar_rolagens, name='listar_rolagens'),
    path('api/rolagem/limpar/', views.limpar_log, name='limpar_log'), 

    # --- CRUD DE MESAS ---
    path('mesas/', views.lista_mesas, name='lista_mesas'),
    path('mesas/nova/', views.criar_mesa, name='criar_mesa'),

    # --- CRUD DE PERSONAGENS ---
    path('personagens/', views.lista_personagens, name='lista_personagens'),
    path('personagens/novo/', views.criar_personagem, name='criar_personagem'),
    path('personagens/editar/<int:pk>/', views.editar_personagem, name='editar_personagem'),
    path('personagens/excluir/<int:pk>/', views.excluir_personagem, name='excluir_personagem'),

    # --- INVENTÁRIO ---
    path('personagem/<int:pk>/inventario/', views.gerenciar_inventario, name='gerenciar_inventario'),
    
    # --- CRUD DE ITENS ---
    path('itens/', views.lista_itens, name='lista_itens'),
    path('itens/novo/', views.criar_item, name='criar_item'),

    # ========== SISTEMA DE COMBATE ==========
    path('combate/iniciar/<int:mesa_id>/', views.iniciar_combate, name='iniciar_combate'),
    path('combate/<int:combate_id>/', views.sala_combate, name='sala_combate'),
    path('combate/<int:combate_id>/acao/', views.acao_combate, name='acao_combate'),
    path('combate/<int:combate_id>/adicionar-monstro/', views.adicionar_monstro, name='adicionar_monstro'),
    path('combate/<int:combate_id>/status/', views.status_combate, name='status_combate'),

    # ========== CHAT EM TEMPO REAL ==========
    path('chat/<int:mesa_id>/', views.chat_mesa, name='chat_mesa'),

    # ========== SISTEMA DE MISSÕES ==========
    path('mesa/<int:mesa_id>/missoes/', views.lista_missoes, name='lista_missoes'),
    path('mesa/<int:mesa_id>/missoes/criar/', views.criar_missao, name='criar_missao'),
    path('missoes/<int:missao_id>/', views.detalhes_missao, name='detalhes_missao'),
    path('missoes/<int:missao_id>/progresso/', views.atualizar_progresso_missao, name='atualizar_progresso_missao'),
    path('missoes/<int:missao_id>/concluir/', views.concluir_missao, name='concluir_missao'),

    # ========== SISTEMA DE NOTIFICAÇÕES ==========
    path('notificacoes/', views.lista_notificacoes, name='lista_notificacoes'),
    path('api/notificacoes/nao-lidas/', views.api_notificacoes_nao_lidas, name='api_notificacoes_nao_lidas'),
    path('api/notificacoes/marcar-todas-lidas/', views.api_marcar_todas_lidas, name='api_marcar_todas_lidas'),

    # ========== DASHBOARD DO MESTRE ==========
    path('mestre/dashboard/<int:mesa_id>/', views.dashboard_mestre, name='dashboard_mestre'),
    path('api/mestre/curar/<int:mesa_id>/<int:personagem_id>/', views.api_mestre_curar_personagem, name='api_mestre_curar_personagem'),
    path('api/mestre/status/<int:mesa_id>/', views.api_mestre_status_personagens, name='api_mestre_status_personagens'),
]