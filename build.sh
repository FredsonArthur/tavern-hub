#!/usr/bin/env bash
# Saia se houver erro
set -o errexit

# Instala as dependências
pip install -r requirements.txt

# Prepara os arquivos estáticos (essencial para Django em produção)
python manage.py collectstatic --no-input

# Aplica as migrações no seu banco do Supabase
python manage.py migrate