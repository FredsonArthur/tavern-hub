from django.db import migrations
from django.contrib.auth import get_user_model
import os

def criar_admin(apps, schema_editor):
    User = get_user_model()
    # Pega valores das variáveis de ambiente que você configurou no Render
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@tavern.hub')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)

class Migration(migrations.Migration):

    dependencies = [
        # IMPORTANTE: Verifique o nome da sua migração anterior na pasta migrations
        ('lobby', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(criar_admin),
    ]