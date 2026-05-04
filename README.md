# 🎲 TavernHub: O Lobby de Sessão Interativo

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard onde jogadores e mestres sincronizam rolagens de dados e gerenciam personagens, unindo o poder do **Django** com a interatividade do **JavaScript**[cite: 3, 6].

---

## 🛠️ Tecnologias Integradas

* **Backend:** Python 3.13+ & Django 6.0+[cite: 2, 5]
* **Frontend:** JavaScript Moderno (Vanilla), HTML5, CSS3 & Bootstrap 5[cite: 6]
* **Gestão de Dados:** SQLite (Desenvolvimento) com suporte a Migrations (ORM Django)
* **Arquitetura:** MVC (Model-View-Controller) & **Publish-Subscribe (Django Signals)**[cite: 3]
* **Qualidade:** Testes Automatizados (Django TestCase)[cite: 4]

---

## 🎯 Funcionalidades & Progresso

### Fase 1: O Tabuleiro Estático & Persistência (Concluída ✅)
- [x] Setup inicial do projeto Django e App Lobby[cite: 2].
- [x] Configuração de ambiente virtual (venv) e segurança (.gitignore)[cite: 2].
- [x] Interface com Widget de múltiplos dados (D4 a D100).
- [x] Conexão Front-End -> Back-End via Fetch API/JSON[cite: 5].
- [x] Log de Atividades com **Internacionalização (Brasília/UTC-3)**[cite: 6].

### Fase 2: O Coração do RPG - CRUD & Entidades (Concluída ✅)
- [x] **Gestão de Mesas (Entidade 1):** CRUD para criação e listagem de mesas[cite: 6].
- [x] **Gestão de Personagens (Entidade 2):** CRUD completo (Criar, Consultar, Editar e Excluir)[cite: 3, 6].
- [x] **Sistema de Rolagens (Entidade 3):** Registro persistente com função de limpeza de log (Delete)[cite: 4, 6].
- [x] **Integração de Entidades:** Vínculo real entre Personagem -> Mesa e Rolagem -> Personagem[cite: 3, 6].
- [x] **Paradigma Publish-Subscribe:** Implementação de Signals para monitoramento de eventos (ex: Críticos)[cite: 3, 4].
- [x] **Suíte de Testes:** Validação automatizada de rotas e integridade de dados[cite: 4].

### Fase 3: A Magia do Tempo Real (Próximos Passos 🚧)
- [ ] Sincronização de rolagens via WebSockets (Django Channels).
- [ ] Sistema de Iniciativa (Tracker) ordenável.
- [ ] Implementação de Django Messages para feedback visual de ações (UX).
- [ ] Integração de notas rápidas exportáveis para o Obsidian.

---

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar o sistema (essencial para avaliação):

1. **Clonar o repositório:**
   ```bash
   git clone <link-do-seu-repo>
   cd tavern-hub