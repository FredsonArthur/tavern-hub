# 🏰 TavernHub — O Lobby de Sessão Interativo para RPG

[![Python Version](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-6.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![OS](https://img.shields.io/badge/OS-Ubuntu_Linux-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard em tempo real onde jogadores e mestres sincronizam rolagens de dados e gerenciam personagens, unindo a robustez do ecossistema **Django** com a interatividade de scripts **JavaScript** customizados.

O sistema gerencia mesas de jogo e os seus respectivos personagens através de regras de negócio complexas, como exclusão lógica (*Soft Delete*), consistência de fuso horário internacional e relacionamentos automatizados via ORM nativo.

---

## 🛠️ Tecnologias e Configurações de Ambiente

| Componente | Tecnologia Empregada | Detalhes de Implementação |
| :--- | :--- | :--- |
| **Backend** | Python 3.13+ / Django 6.0+ | Arquitetura MVT robusta e persistência com ORM nativo. |
| **Frontend** | Vanilla JS / Bootstrap 5 | Interface interativa com conexão via Fetch API/JSON. |
| **Gestão de Dados**| SQLite | Suporte completo a Migrations e relacionamentos complexos. |
| **Arquitetura** | Publish-Subscribe | Implementação de **Django Signals** para reatividade assíncrona. |
| **Timezone** | `America/Sao_Paulo` | Log de atividades sincronizado com o Horário de Brasília (UTC-3). |
| **Qualidade** | Django TestCase | Suíte completa com 100% de aprovação nos testes integrados. |

---

## 🏗️ Arquitetura do Sistema e Estrutura de Pastas

O projeto segue o padrão estrutural rígido do framework Django, separando responsabilidades lógicas e organizando os componentes sob o app core `lobby`:

```text
tavern-hub/
├── tavern_hub/             # Diretório de configurações do projeto global
│   ├── settings.py         # Configurações de banco, fuso horário e segurança
│   └── urls.py             # Roteamento global de endpoints do sistema
├── lobby/                  # Aplicativo principal do ecossistema do jogo
│   ├── models.py           # Modelos de dados mapeados no ORM (Personagem, Mesa, Item)
│   ├── views.py            # Lógica de controle e renderização de requisições HTTP
│   ├── signals.py          # Gatilhos automatizados e inteligência de dados
│   ├── tests.py            # Suíte de blindagem e validação automatizada de software
│   └── urls.py             # Rotas internas dinâmicas do aplicativo
└── manage.py               # Utilitário de gerenciamento e execução de comandos
```

## 🎯 Funcionalidades & Progresso do Projeto

### 📦 Fase 1: O Tabuleiro Estático & Persistência `(Concluída ✅)`
- [x] **Setup Inicial:** Configuração do projeto Django e estruturação do App Lobby.
- [x] **Widget de Dados:** Interface interativa contendo múltiplos tipos de dados para rolagem (D4 a D100).
- [x] **Comunicação Assíncrona:** Integração assíncrona Front-End e Back-End estabelecida através de chamadas estruturadas na Fetch API com tráfego de dados via JSON.
- [x] **Log de Atividades:** Registro de logs com tratamento completo de fuso horário e **Internacionalização para o Horário de Brasília (UTC-3)**.

### 👥 Fase 2: O Coração do RPG - CRUD & Entidades `(Concluída ✅)`
- [x] **Gestão de Mesas:** Mapeamento e CRUD completo para criação, leitura e listagem de mesas de jogo ativas.
- [x] **Gestão de Personagens:** CRUD operacional contendo as rotas de Criação, Consulta, Edição e Exclusão de fichas.
- [x] **Integração de Entidades:** Arquitetura de banco configurada para permitir a vinculação dinâmica e em tempo real de múltiplos personagens a mesas distintas.

### ⚡ Fase 3: Arquitetura Assíncrona & Lógica de Jogo `(Concluída ✅)`
- [x] **Soft Delete de Personagens:** Mecanismo de exclusão lógica implementado por meio de flags booleanas no banco, impedindo a perda de dados históricos e mantendo a integridade referencial.
- [x] **Paradigma Publish-Subscribe (Signals):** Acoplamento de gatilhos automatizados via Django Signals para monitoramento imediato de rolagens críticas e geração automática de logs de auditoria impressos diretamente no terminal do servidor.
- [x] **API com Filtros Dinâmicos:** Criação e refinamento de endpoints legíveis que aceitam filtros parametrizados via URL para segmentação por tipo de dado.

### 🔐 Fase 4: Inteligência de Dados & Segurança `(Concluída ✅)`
- [x] **Painel de Estatísticas (Aggregations):** Emprego de funções agregadoras nativas do banco de dados (`Avg`, `Count` e `Max`) para processamento de médias aritméticas, volumetria e ranking de pontuações de forma performática.
- [x] **Sistema de Rollback (Versionamento):** Lógica estruturada para edições auditáveis de resultados salvando o histórico da rolagem e preservando o valor contido em `resultado_anterior`.
- [x] **Mesa Protegida (Permissões):** Bloqueio de segurança em nível de rotas e visões. O acesso a edições ou rollbacks de jogadas é restrito exclusivamente ao usuário com credenciais de Mestre da mesa.

### 🎒 Fase 5: Expansão de Inventário, UX & Estabilidade `(Concluída ✅)`
- [x] **Gestão de Inventário (Many-to-Many):** Criação da entidade relacional `Item`, configurando uma relação do tipo *Muitos-para-Muitos* que permite que múltiplos personagens portem equipamentos variados e concomitantes.
- [x] **Biblioteca Global de Itens:** Painel dedicado e interface construída com foco na forja rápida, catalogação e listagem geral de itens pertencentes ao cenário do mundo.
- [x] **Sinais de Inteligência:** Desenvolvimento de regras de monitoramento automatizadas via sinais para detecção em tempo real e alerta visual de eventos como "Maré de Azar" (quando ocorrem 3 falhas seguidas) e notificações de "Riqueza".
- [x] **Feedback Visual (Django Messages):** Acoplamento do módulo de mensagens nativas do Django para renderizar alertas visuais flutuantes de sucesso, erros de operação e avisos importantes na interface do usuário.
- [x] **Navegação Consolidada:** Padronização estética baseada em herança estrutural de blocks em templates HTML globais e criação de links rápidos direcionando o gerenciamento do inventário dentro da tela de detalhes do personagem.
- [x] **Suíte de Testes Automatizados:** Cobertura de testes unitários e testes integrados robustos. Validação contendo checagem de Sinais M2M, restrições e travas de segurança de Views e testes de regressão de exclusão lógica (Soft Delete) operando com 100% de aprovação.