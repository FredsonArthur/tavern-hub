from django.contrib import admin
from .models import Mesa, Personagem, Rolagem, Missao, MissaoPersonagem, Notificacao

# Configuração para a Entidade 1: Mesa
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'mestre', 'data_criacao')
    search_fields = ('titulo', 'mestre__username')
    list_filter = ('data_criacao',)

# Configuração para a Entidade 2: Personagem
@admin.register(Personagem)
class PersonagemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'raca', 'classe', 'nivel')
    search_fields = ('nome', 'usuario__username')
    list_filter = ('classe', 'raca', 'nivel')

# Configuração para a Entidade 3: Rolagem
@admin.register(Rolagem)
class RolagemAdmin(admin.ModelAdmin):
    list_display = ('get_identificacao', 'tipo_dado', 'resultado', 'data_hora')
    list_filter = ('tipo_dado', 'data_hora')
    readonly_fields = ('data_hora',)

    def get_identificacao(self, obj):
        return obj.personagem.nome if obj.personagem else obj.jogador_nome
    get_identificacao.short_description = 'Quem Rolou'


# ========== SISTEMA DE MISSÕES ==========

@admin.register(Missao)
class MissaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'mesa', 'status', 'dificuldade', 'data_criacao')
    list_filter = ('status', 'dificuldade', 'mesa')
    search_fields = ('titulo', 'descricao', 'objetivos')


@admin.register(MissaoPersonagem)
class MissaoPersonagemAdmin(admin.ModelAdmin):
    list_display = ('personagem', 'missao', 'progresso', 'concluida')
    list_filter = ('concluida', 'missao')
    search_fields = ('personagem__nome', 'missao__titulo')

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'lida', 'data_criacao')
    list_filter = ('tipo', 'lida', 'data_criacao')
    search_fields = ('titulo', 'mensagem', 'usuario__username')

