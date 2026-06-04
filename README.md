🏰 TavernHub — Lobby de Sessão Interativo para RPG

O TavernHub é uma plataforma robusta para gerenciamento de sessões de RPG, focada em rastreabilidade de dados e comunicação em tempo real entre componentes. O sistema utiliza uma arquitetura baseada em Django (Web) e um microsserviço de persistência paralelo (Node.js), integrados via RabbitMQ para garantir consistência e desacoplamento.
🛠️ Arquitetura e Tecnologias

O projeto adota o padrão Pub-Sub (Publish-Subscribe) para o processamento de rolagens de dados:

    Backend (Web): Django 6.0+ (Python 3.13+)

    Persistence Worker: Node.js (com amqplib)

    Mensageria: RabbitMQ (Broker AMQP)

    Banco de Dados: PostgreSQL (Produção) / SQLite (Desenvolvimento)

    Ambiente: Otimizado para distribuições Linux (Fedora/Debian/Ubuntu)

🚀 Guia de Configuração (Quick Start)
1. Pré-requisitos

Certifique-se de ter instalado no sistema:

    Python 3.13+

    Node.js 20+

    RabbitMQ Server

2. Configurar o Broker RabbitMQ
Bash

# Ative e inicialize o serviço
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
# Verifique o status
sudo systemctl status rabbitmq-server

3. Ambiente Python & Django
Bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

4. Microsserviço de Persistência (Store)

Abra um novo terminal para rodar o consumidor de eventos:
Bash

cd caminho/para/seu/projeto_node/
npm install
node consumidor.js

5. Execução do Servidor Web

No terminal principal (venv ativa):
Bash

python manage.py runserver

Acesse: http://127.0.0.1:8000
🏗️ Funcionalidades Chave

    Sistema de Auditoria: Logs detalhados de todas as rolagens.

    Rollback de Dados: Possibilidade de corrigir resultados de rolagens via painel do Mestre (com marcação histórica de auditoria).

    Soft Delete: Exclusão lógica de personagens e itens, mantendo a integridade dos dados no banco.

    Cache Inteligente: Otimização de consultas estatísticas através de cache de baixo nível do Django.

    Gestão de Inventário: Relacionamentos Many-to-Many para itens, com suporte a raridades (Comum a Lendário).

🧪 Suíte de Testes

Para validar a integridade estrutural e evitar regressões:
Bash

python manage.py test

Projeto desenvolvido com foco em alta disponibilidade e consistência de dados em sessões de RPG.