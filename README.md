# 🏰 TavernHub — Lobby de Sessão Interativo para RPG

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-20+-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13+-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

---

## 📖 Sobre o Projeto

**TavernHub** é uma plataforma robusta para gerenciamento de sessões de RPG, focada em rastreabilidade de dados e comunicação em tempo real entre componentes. O sistema utiliza uma arquitetura baseada em **Django** e um **microsserviço de persistência paralelo (Node.js)**, integrados via **RabbitMQ** para garantir consistência e desacoplamento.

> 🎲 *"Que os dados estejam sempre a seu favor!"*

---

## 🏗️ Arquitetura do Sistema
+-----------------------------------------------------------------------------------+
| 🌐 USUÁRIOS (Browser) |
+----------------------------------------+------------------------------------------+
|
v
+----------------------------------------+------------------------------------------+
| 🐍 Django (Web - Gunicorn) |
| +------------+ +------------+ +------------+ +------------+ |
| |🔐 Login | |👥 Persona- | |🏰 Mesas | |📦 Itens | |
| | /Registro | | gens | | (CRUD) | | (M2M) | |
| +------------+ +------------+ +------------+ +------------+ |
| | | |
| v v |
| +--------------------+ +--------------------+ |
| | 💾 Cache | | 📨 RabbitMQ | |
| | (Database) | | Publisher | |
| +--------------------+ +---------+----------+ |
+--------------------------------------------------------+----------------------------+
|
v
+--------------------------------------------------------+----------------------------+
| 🟢 Microsserviço Node.js (Consumer) |
| - Escuta filas RabbitMQ |
| - Persiste logs de rolagens |
| - Auditoria e rollback |
+--------------------------------------------------------+----------------------------+
|
v
+--------------------------------------------------------+----------------------------+
| 🐘 PostgreSQL (Dados Persistentes) |
+-------------------------------------------------------------------------------------+

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Versão | Ícone |
|-----------|------------|--------|-------|
| **Backend** | Django | 5.2+ | 🐍 |
| **Backend** | Python | 3.13+ | 🐍 |
| **Microsserviço** | Node.js | 20+ | 🟢 |
| **Mensageria** | RabbitMQ | 3.13+ | 📨 |
| **Banco de Dados** | PostgreSQL | 15+ | 🐘 |
| **Cache** | Database Cache | - | 💾 |
| **Frontend** | Bootstrap | 5.3 | 🎨 |
| **Frontend** | FontAwesome | 6.0 | ✨ |
| **Frontend** | Animate.css | 4.1 | 🎬 |
| **Autenticação** | Django Auth | - | 🔐 |
| **CI/CD** | GitHub Actions | - | ⚡ |
| **Deploy** | Render / AWS | - | ☁️ |

---

## ✨ Funcionalidades

### 🎲 Sistema de Rolagens
- Rolagem de dados (D4, D6, D8, D10, D12, D20) com animações
- Publicação de eventos via RabbitMQ (Pub/Sub)
- Log em tempo real com WebSocket

### 👥 Gerenciamento de Personagens
- **Atributos completos**: Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma
- **Modificadores automáticos** baseados nas regras D&D
- **Sistema de XP** e progressão de nível
- **Soft Delete** - exclusão lógica com possibilidade de restauração

### 🏰 Mesas de RPG
- CRUD completo de campanhas
- Estatísticas de personagens e rolagens por mesa
- Painel do Mestre com controle de auditoria

### 📦 Inventário e Itens
- Sistema **Many-to-Many** para equipamentos
- 5 níveis de raridade: Comum, Incomum, Raro, Épico, Lendário
- Cálculo de peso total e distribuição por raridade

### 📊 Estatísticas e Cache
- Painel com métricas agregadas (total, média, recorde)
- **Cache de baixo nível** para otimização de consultas
- Ranking de jogadores mais ativos

### 🔄 Auditoria e Rollback
- Histórico completo de rolagens
- Correção de resultados com registro de motivo
- Marcação de "Editado por Mestre" nas crônicas

### 🔐 Autenticação
- Cadastro e login de usuários
- Validação de senha com requisitos de segurança
- Proteção de rotas com `@login_required`

---

## 🚀 Guia de Configuração (Quick Start)

### 1️⃣ Pré-requisitos

Certifique-se de ter instalado no sistema:

| Requisito | Versão | Comando para verificar |
|-----------|--------|------------------------|
| 🐍 Python | 3.13+ | `python --version` |
| 🟢 Node.js | 20+ | `node --version` |
| 📨 RabbitMQ | 3.13+ | `rabbitmqctl status` |
| 🐘 PostgreSQL | 15+ | `psql --version` |

### 2️⃣ Configurar o Broker RabbitMQ

```bash
# Ative e inicialize o serviço
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Verifique o status
sudo systemctl status rabbitmq-server
```
## Ambiente Python & Django
### Clone o repositório
git clone https://github.com/FredsonArthur/tavern-hub.git
cd tavern-hub

### Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
### venv\Scripts\activate   # Windows

### Instale as dependências
pip install -r requirements.txt

### Configure variáveis de ambiente (copie o exemplo)
cp .env.example .env
### Edite o .env com suas configurações

### Execute as migrações
python manage.py migrate
python manage.py createcachetable

### Crie um superusuário (administrador)
python manage.py createsuperuser

Configurar Banco de Dados (PostgreSQL)
### Usando Docker (recomendado)
docker-compose up -d

### Ou configure manualmente no .env
### DATABASE_URL=postgresql://usuario:senha@localhost:5432/tavernhub

Microsserviço de Persistência (Store)
### Abra um novo terminal
cd microservico-pubsub
npm install
npm start
### ou
node consumer.js

Execução do Servidor Web
### No terminal principal (venv ativa)
python manage.py runserver

## 🧪 Suíte de Testes
Para validar a integridade estrutural e evitar regressões:
### Executar todos os testes
python manage.py test

### Testes específicos do app lobby
python manage.py test lobby

### Com maior verbosidade
python manage.py test --verbosity=2

## 📁 Estrutura do Projeto
tavern-hub/
├── core/                    # Configurações Django
│   ├── settings.py          # Configurações (com suporte a .env)
│   ├── urls.py              # Rotas principais
│   └── asgi.py / wsgi.py    # Servidores ASGI/WSGI
├── lobby/                   # App principal
│   ├── models.py            # Entidades: Mesa, Personagem, Item, Rolagem
│   ├── views.py             # CRUD + APIs + Cache + Rollback
│   ├── forms.py             # Formulários com choices
│   ├── signals.py           # Sinais (críticos, maré de azar)
│   ├── messaging.py         # Publisher RabbitMQ
│   └── templates/lobby/     # 15+ templates estilizados
├── microservico-pubsub/     # Microsserviço Node.js
│   ├── consumer.js          # Consumidor RabbitMQ
│   └── package.json
├── static/                  # Arquivos estáticos
├── .env.example             # Exemplo de variáveis de ambiente
├── docker-compose.yml       # PostgreSQL + RabbitMQ
├── requirements.txt         # Dependências Python
└── README.md                # Este arquivo

## 📊 Diagrama ER (Entidades)
+-------------+     +-------------+     +-------------+
|    User     |     |    Mesa     |     | Personagem  |
+-------------+     +-------------+     +-------------+
| id (PK)     |-----<| id (PK)     |     | id (PK)     |
| username    |     | titulo      |-----<| nome        |
| email       |     | descricao   |     | raca        |
| password    |     | mestre (FK) |     | classe      |
+-------------+     | data_criacao|     | nivel       |
                    +-------------+     | forca       |
                                        | destreza    |
+-------------+     +-------------+     | constituicao|
|    Item     |     |  Rolagem    |     | inteligencia|
+-------------+     +-------------+     | sabedoria   |
| id (PK)     |     | id (PK)     |     | carisma     |
| nome        |     | resultado   |     | vida_atual  |
| raridade    |     | tipo_dado   |     | xp          |
| peso        |     | editado     |     | ativo (SD)  |
| ativo (SD)  |     | motivo      |     +-------------+
+-------------+     +-------------+
     |                    |
     | (M2M)              | (FK)
     v                    v
+---------------------------------------------------+
|                personagem_itens                   |
|            (Tabela pivô Many-to-Many)             |
+---------------------------------------------------+

## 📝 Licença

Projeto desenvolvido para fins acadêmicos e demonstração de arquitetura Pub/Sub com Django e Node.js.