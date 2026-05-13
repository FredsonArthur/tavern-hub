# 🎲 TavernHub: O Lobby de Sessão Interativo

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard onde jogadores e mestres sincronizam rolagens de dados e gerenciam personagens, unindo o poder do **Django** com a interatividade do **JavaScript**.

---

## 🛠️ Tecnologias Integradas

* **Backend:** Python 3.13+ & Django 6.0+
* **Frontend:** JavaScript Moderno (Vanilla), HTML5, CSS3 & Bootstrap 5
* **Gestão de Dados:** SQLite (Desenvolvimento) com suporte a Migrations (ORM Django)
* **Arquitetura:** MVC (Model-View-Controller) & **Publish-Subscribe (Django Signals)**
* **Qualidade:** Testes Automatizados (Django TestCase)

---

## 🎯 Funcionalidades & Progresso

### Fase 1: O Tabuleiro Estático & Persistência (Concluída ✅)
- [x] Setup inicial do projeto Django e App Lobby.
- [x] Configuração de ambiente virtual (venv) e segurança (.gitignore).
- [x] Interface com Widget de múltiplos dados (D4 a D100).
- [x] Conexão Front-End -> Back-End via Fetch API/JSON.
- [x] Log de Atividades com **Internacionalização (Brasília/UTC-3)**.

### Fase 2: O Coração do RPG - CRUD & Entidades (Concluída ✅)
- [x] **Gestão de Mesas (Entidade 1):** CRUD para criação e listagem de mesas.
- [x] **Gestão de Personagens (Entidade 2):** CRUD completo (Criar, Consultar, Editar e Excluir).
- [x] **Sistema de Rolagens (Entidade 3):** Registro persistente com função de limpeza de log (Delete).
- [x] **Integração de Entidades:** Vínculo real entre Personagem -> Mesa e Rolagem -> Personagem.

### Fase 3: Lógica Avançada & Auditoria (Concluída ✅)
- [x] **Soft Delete de Personagens:** Implementação de exclusão lógica para manutenção de integridade.
- [x] **Paradigma Publish-Subscribe (Signals):** Monitoramento automático de críticos e logs de auditoria no terminal.
- [x] **API com Filtros Dinâmicos:** Refinamento da leitura permitindo filtragem por tipo de dado via URL.

### Fase 4: Inteligência de Dados & Segurança (Concluída ✅)
- [x] **Painel de Estatísticas (Aggregations):** Uso de `Avg`, `Count` e `Max` para processar médias e ranking diretamente no banco.
- [x] **Sistema de Rollback (Versionamento):** Edição auditável de rolagens preservando o `resultado_anterior`.
- [x] **Mesa Protegida (Permissões):** Restrição de acesso. Apenas o Mestre possui permissão para Rollbacks e gestão crítica.

### Fase 5: Expansão de Inventário & UX (Concluída ✅)
- [x] **Gestão de Inventário (Many-to-Many):** Nova entidade `Item` que permite personagens possuírem múltiplos equipamentos.
- [x] **Inteligência de Sinais Avançada:** Detecção automática de "Maré de Azar" (3 falhas seguidas) e alerta de "Riqueza".
- [x] **Feedback Visual (Django Messages):** Implementação de alertas dinâmicos de sucesso, erro e avisos na interface (UX).
- [x] **Interface de Inventário:** Novo dashboard para equipar e visualizar itens valiosos.

### Próximos Passos 🚧
- [ ] Sincronização de rolagens via WebSockets (Django Channels).
- [ ] Sistema de Iniciativa (Tracker) ordenável.
- [ ] Integração de notas rápidas exportáveis para o Obsidian.

---

## 🚀 Como Executar o Projeto Localmente (Linux/VS Code)

1. **Clonar o repositório:**
   ```bash
   git clone <link-do-seu-repo>
   cd tavern-hub