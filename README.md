# 🏰 TavernHub — Lobby de Sessão Interativo para RPG

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-20+-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13+-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)

---

## 🏰 Sobre o Projeto

**TavernHub** é uma plataforma completa para gerenciamento de sessões de RPG, com rolagem de dados, chat em tempo real, combates, missões e painel de controle para o mestre.

> 🎲 *"Que os dados estejam sempre a seu favor!"*

---

## ✨ Funcionalidades

| Categoria | Funcionalidades |
|-----------|-----------------|
| 🎲 **Rolagens** | D4 a D20, críticos, rollback com auditoria, RabbitMQ |
| 👥 **Personagens** | Atributos, XP, níveis, soft delete, inventário M2M |
| 🏰 **Mesas** | CRUD completo, chat por mesa, estatísticas |
| ⚔️ **Combate** | Turnos, iniciativa, ações, monstros, histórico |
| 📋 **Missões** | Criação, progresso individual, recompensas |
| 👑 **Mestre** | Dashboard, cura/dano, visão geral da mesa |
| 🔔 **Notificações** | Alertas em tempo real, badge de não lidas |
| 💬 **Chat** | WebSockets, comandos `/rolar`, mensagens em tempo real |

---

## 🛠️ Tecnologias

| Categoria | Tecnologias |
|-----------|-------------|
| 🐍 **Backend** | Python 3.13+, Django 5.2+, Django Channels |
| 🟢 **Microsserviço** | Node.js 20+, amqplib |
| 📨 **Mensageria** | RabbitMQ 3.13+, Pika |
| 🗄️ **Banco de Dados** | PostgreSQL 15+, SQLite, Redis |
| 🎨 **Frontend** | Bootstrap 5.3, FontAwesome 6, Animate.css |
| ⚡ **Infra** | GitHub Actions, Docker, Gunicorn, Daphne |

---

## 🚀 Guia de Configuração

### Pré-requisitos
- Python 3.13+, Node.js 20+, RabbitMQ 3.13+, PostgreSQL 15+, Redis 7+

### Passo a passo

# 1. Clone e entre no projeto
     git clone https://github.com/FredsonArthur/tavern-hub.git
     cd tavern-hub

# 2. Crie ambiente virtual e instale dependências
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt

# 3. Configure variáveis de ambiente
     cp .env.example .env
# Edite o .env com suas configurações

# 4. Execute migrações e crie superusuário
     python manage.py migrate
     python manage.py createcachetable
     python manage.py createsuperuser

# 5. Inicie o RabbitMQ e Redis
     sudo systemctl start rabbitmq-server
     sudo systemctl start redis-server

# 6. Rode o microsserviço (em outro terminal)
     cd microservico-pubsub
     npm install
     node consumer.js

# 7. Rode o servidor Django
     daphne -p 8000 core.asgi:application
     Acesse: http://127.0.0.1:8000/
## 🧪 Testes
     python manage.py test
## 🤝 Contribuição

    Faça um fork do projeto

    Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

    Commit suas mudanças (git commit -m 'Add some AmazingFeature')

    Push para a branch (git push origin feature/AmazingFeature)

    Abra um Pull Request
---
## 📝 Licença

     Projeto desenvolvido para fins acadêmicos e demonstração de arquitetura Pub/Sub com Django e Node.js.