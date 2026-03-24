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
- [x] **Conexão Front-End -> Back-End (Salvar rolagens via Fetch API/JSON).**
- [ ] Widget completo de múltiplos dados (D4, D6, D10, D12, D100).
- [ ] Lista de Jogadores online com avatares.

### Fase 2: O Coração do RPG (Interatividade)
- [ ] Log de Atividades (Exibir as últimas rolagens na tela para os jogadores).
- [ ] Chat da taverna com suporte a Markdown.
- [ ] Sistema de Iniciativa (Tracker) ordenável.
- [ ] Painel do Mestre (DM Screen) para controle de NPCs.

### Fase 3: A Magia do Tempo Real
- [ ] Sincronização de rolagens via WebSockets (Django Channels).
- [ ] Efeitos visuais no Canvas para acertos críticos.
- [ ] Integração de notas rápidas exportáveis para o **Obsidian**.

---

## 📝 Notas de Desenvolvimento
O projeto validou com sucesso a comunicação assíncrona entre o navegador e o servidor. O próximo desafio é transformar os dados salvos em um "Log de Combate" visual para que a interface reflita o histórico do banco de dados em tempo real.