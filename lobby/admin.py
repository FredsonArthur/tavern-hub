from django.contrib import admin
from .models import Mesa, Personagem, Rolagem

# Configuração para a Entidade 1: Mesa
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'mestre', 'data_criacao')  # Colunas que aparecem na lista
    search_fields = ('titulo', 'mestre__username')      # Barra de busca por título ou mestre
    list_filter = ('data_criacao',)                     # Filtro lateral por data

# Configuração para a Entidade 2: Personagem
@admin.register(Personagem)
class PersonagemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'raca', 'classe', 'nivel') # Visão geral do herói
    search_fields = ('nome', 'usuario__username')                 # Busca por nome do char ou dono[cite: 15]
    list_filter = ('classe', 'raca', 'nivel')                     # Filtros de RPG[cite: 15]

# Configuração para a Entidade 3: Rolagem
@admin.register(Rolagem)
class RolagemAdmin(admin.ModelAdmin):
    list_display = ('get_identificacao', 'tipo_dado', 'resultado', 'data_hora') # Log detalhado[cite: 15]
    list_filter = ('tipo_dado', 'data_hora')                                   # Filtro por dado ou tempo[cite: 15]
    readonly_fields = ('data_hora',)                                           # Impede editar a hora da sorte[cite: 15]

    def get_identificacao(self, obj):
        """Exibe o nome do personagem vinculado ou o nome manual do log."""
        return obj.personagem.nome if obj.personagem else obj.jogador_nome
    get_identificacao.short_description = 'Quem Rolou'