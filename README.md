# 🎲 TavernHub: O Lobby de Sessão Interativo

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard em tempo real onde jogadores e mestre podem sincronizar rolagens de dados, status de personagens e notas rápidas, unindo o poder do **Django** com a interatividade do **JavaScript**.

---

## 🛠️ Tecnologias Integradas

* **Backend:** Python 3.13+ & Django 6.0+
* **Frontend:** JavaScript Moderno (Vanilla), HTML5 & CSS3
* **Gestão de Dados:** SQLite (Desenvolvimento) com suporte a Migrations (ORM Django)
* **Ferramentas de Dev:** VS Code, GitHub Desktop & venv (Ambiente Virtual)

---

## 🎯 Funcionalidades & Progresso

### Fase 1: O Tabuleiro Estático & Persistência (MVP)
- [x] Setup inicial do projeto Django e App Lobby.
- [x] Configuração de ambiente virtual (venv) e segurança de repositório (.gitignore).
- [x] Criação da View de Dashboard e rota principal.
- [x] Interface inicial com botão de Rolagem de Dados (D20 via JS).
- [x] Modelagem de Banco de Dados para persistência de rolagens.
- [x] Registro no Admin do Django para controle do mestre.
- [x] Conexão Front-End -> Back-End (Salvar rolagens via Fetch API/JSON).
- [x] Log de Atividades (Exibição das últimas rolagens na tela para os jogadores).
- [x] Identificação de Jogador (Captura de nome via interface e salvamento dinâmico).
- [x] Widget completo de múltiplos dados (D4, D6, D8, D10, D12, D20, D100).
- [x] **Internacionalização e Ajuste de Fuso Horário (Brasília/UTC-3).**
- [ ] Lista de Jogadores online com avatares.

### Fase 2: O Coração do RPG (Interatividade)
- [ ] Chat da taverna com suporte a Markdown.
- [ ] Sistema de Iniciativa (Tracker) ordenável.
- [ ] Painel do Mestre (DM Screen) para controle de NPCs.

### Fase 3: A Magia do Tempo Real
- [ ] Sincronização de rolagens via WebSockets (Django Channels).
- [ ] Efeitos visuais no Canvas para acertos críticos.
- [ ] Integração de notas rápidas exportáveis para o **Obsidian**.

---

## 📝 Notas de Desenvolvimento
O sistema agora suporta a gama completa de dados de RPG (D4 a D100) e possui um Log de Combate detalhado que inclui o nome do jogador, o tipo de dado e a estampa de tempo (timestamp) formatada com data e hora local de Brasília (America/Sao_Paulo). A arquitetura utiliza `timezone.localtime` para garantir que a interface web reflita o horário real dos jogadores, independentemente do armazenamento em UTC no banco de dados.