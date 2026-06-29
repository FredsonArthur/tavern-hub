#!/usr/bin/env bash
# O comando 'set -o errexit' faz o script sair imediatamente se qualquer comando falhar
set -o errexit

# 1. Instala as dependências a partir do requirements.txt
echo "Instalando dependências..."
pip install --no-cache-dir -r requirements.txt

# 2. Coleta os arquivos estáticos
# O WhiteNoise precisa deste comando para organizar os arquivos na pasta staticfiles/
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# 3. Aplica as migrações no banco de dados do Supabase
echo "Aplicando migrações..."
python manage.py migrate --no-input