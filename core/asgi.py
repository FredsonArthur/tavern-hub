import os
from django.core.asgi import get_asgi_application

# CORRIGIDO: De core.settings para tavern_hub.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tavern_hub.settings')

application = get_asgi_application()