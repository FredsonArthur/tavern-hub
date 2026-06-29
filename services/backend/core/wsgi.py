import os

from django.core.wsgi import get_wsgi_application

# Aponta para as configurações do diretório core
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()