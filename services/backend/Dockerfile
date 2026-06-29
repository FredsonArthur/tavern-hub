FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

RUN chmod +x build.sh

# Expõe a porta do Django
EXPOSE 8000

CMD ["sh", "-c", "./build.sh && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]
