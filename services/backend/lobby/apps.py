from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class LobbyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lobby'
    verbose_name = _('Sistema de TavernHub')

    def ready(self):
        """
        Método chamado quando o Django termina de carregar a aplicação.
        Aqui importamos os sinais para ativar o paradigma Publish-Subscribe.
        A verificação try/except garante que a importação não falhe se o arquivo
        tiver erros de sintaxe ou dependências faltantes.
        """
        try:
            import lobby.signals
        except ImportError:
            pass