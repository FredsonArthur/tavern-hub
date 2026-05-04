# 🎲 TavernHub: O Lobby de Sessão Interativo

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard em tempo real onde jogadores e mestre podem sincronizar rolagens de dados e gerenciar personagens, unindo o poder do **Django** com a interatividade do **JavaScript**[cite: 3, 6].

---

## 🛠️ Tecnologias Integradas

* **Backend:** Python 3.13+ & Django 6.0+[cite: 2, 5]
* **Frontend:** JavaScript Moderno (Vanilla), HTML5, CSS3 & **Bootstrap 5**[cite: 6, 11]
* **Gestão de Dados:** SQLite (Desenvolvimento) com suporte a Migrations (ORM Django)[cite: 3]
* **Qualidade de Software:** **Testes Automatizados (Django TestCase)**[cite: 4]
* **Ferramentas de Dev:** Cloud9 IDE, GitHub & venv (Ambiente Virtual)[cite: 2]

---

## 🎯 Funcionalidades & Progresso

### Fase 1: O Tabuleiro Estático & Persistência (Concluída ✅)
- [x] Setup inicial do projeto Django e App Lobby[cite: 2, 5].
- [x] Modelagem de Banco de Dados para persistência de rolagens[cite: 3].
- [x] Log de Atividades com ajuste de fuso horário (Brasília/UTC-3)[cite: 6].
- [x] Widget completo de múltiplos dados (D4 a D100)[cite: 11].

### Fase 2: O Coração do RPG - CRUD & Entidades (Concluída ✅)
- [x] **Gestão de Personagens (Entidade Personagem):** CRUD completo (Criar, Listar, Editar e Excluir) vinculado ao usuário autenticado[cite: 3, 6].
- [x] **Gestão de Mesas (Entidade Mesa):** Sistema para mestres criarem e gerenciarem suas mesas de jogo[cite: 3, 6, 9].
- [x] **Sistema de Autenticação:** Proteção de rotas com `@login_required` para segurança dos dados dos jogadores[cite: 6, 9].
- [x] **Admin Customizado:** Painel administrativo configurado para supervisão total das três entidades principais[cite: 1, 3].
- [x] **Testes Automatizados:** Implementação de `TestCase` para validar rotas, modelos e formulários[cite: 4].

### Fase 3: A Magia do Tempo Real (Próximos Passos 🚧)
- [ ] Vincular Rolagem diretamente ao Personagem selecionado no Dashboard.
- [ ] Sincronização de rolagens via WebSockets (Django Channels).
- [ ] Painel do Mestre (DM Screen) para controle de NPCs.

---

## 📝 Notas de Desenvolvimento

A arquitetura do sistema foi evoluída para suportar relacionamentos complexos entre três entidades fundamentais exigidas para o projeto: **Mesa**, **Personagem** e **Rolagem**[cite: 3].

* **Segurança e UX:** O uso de templates base com `{% block content %}` e Bootstrap 5 garante uma interface responsiva, profissional e segura contra acessos não autorizados[cite: 6, 11].
* **Confiabilidade:** O projeto conta com uma suíte de testes automatizados (`tests.py`) que valida as operações de banco de dados e a integridade das URLs, garantindo que o núcleo do sistema permaneça funcional após cada commit[cite: 4].
* **Internacionalização:** Todas as estampas de tempo (timestamps) são convertidas para o horário local de Brasília, garantindo a precisão do log de combate para usuários brasileiros[cite: 6].