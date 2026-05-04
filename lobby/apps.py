from django.apps import AppConfig

class LobbyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lobby'

    def ready(self):
        """
        Método chamado quando o Django termina de carregar a aplicação.
        Aqui importamos os sinais para ativar o paradigma Publish-Subscribe.
        """
        import lobby.signals