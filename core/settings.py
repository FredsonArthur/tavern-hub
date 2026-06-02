from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(^ma1_napt#0zamw!2c7lx^0@3&bzj694byq5l7+$v%fgr57q_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = [
    '.amazonaws.com', 
    'localhost', 
    '127.0.0.1',
    '500cdd641c694620a1c52a6adfc7676c.vfs.cloud9.us-east-1.amazonaws.com'
]

# Configuração para o Cloud9 aceitar o Login
CSRF_TRUSTED_ORIGINS = [
    'https://*.cloud9.us-east-1.amazonaws.com',
    'https://*.amazonaws.com'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lobby',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# --- REQUISITO (ii): Configuração do Banco de Dados PostgreSQL ---
# Configurado dinamicamente para aceitar variáveis de ambiente no fluxo de CI/CD
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tavern_db',
        'USER': 'postgres',
        # Tenta ler a variável injetada pelo GitHub Actions; se não achar, usa a sua local '1234567890'
        'PASSWORD': os.environ.get('DB_PASSWORD', '1234567890'), 
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CONFIGURAÇÕES DE REDIRECIONAMENTO DE AUTENTICAÇÃO ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# --- REQUISITO (viii): Configuração da Estratégia de Cache ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tavern_cache_table',  # Nome da tabela de cache criada no Postgres
        'TIMEOUT': 300,                     # Tempo padrão de armazenamento: 5 minutos (300 segundos)
    }
}