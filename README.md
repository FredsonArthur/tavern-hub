# 🎲 TavernHub: O Lobby de Sessão Interativo

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard em tempo real onde jogadores e mestre podem sincronizar rolagens de dados, status de personagens e notas rápidas, unindo o poder do **Django** com a interatividade do **JavaScript**.

---

## 🛠️ Tecnologias Integradas

* **Backend:** Python 3.12+ & Django Framework
* **Frontend:** JavaScript Moderno (Vanilla), HTML5 & CSS3
* **Comunicação:** WebSockets (Django Channels) para tempo real
* **Gestão de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção)
* **Ferramentas de Dev:** VS Code, GitHub Desktop & Obsidian (para logs de campanha)

---

## 🎯 Funcionalidades Planejadas

### Fase 1: O Tabuleiro Estático (MVP)
- [ ] Dashboard principal com grid responsivo.
- [ ] Widget de Rolagem de Dados (D4, D6, D8, D10, D12, D20, D100).
- [ ] Lista de Jogadores online com avatares customizados.

### Fase 2: O Coração do RPG (Interatividade)
- [ ] Chat da taverna com suporte a Markdown.
- [ ] Sistema de Iniciativa (Tracker) ordenável.
- [ ] Painel do Mestre (DM Screen) para controle de NPCs.

### Fase 3: A Magia do Tempo Real
- [ ] Sincronização de rolagens via WebSockets (todos veem o dado cair!).
- [ ] Efeitos visuais no Canvas para acertos críticos.
- [ ] Integração de notas rápidas exportáveis para o **Obsidian**.