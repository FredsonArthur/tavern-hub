# 🎲 TavernHub: O Lobby de Sessão Interativo

O **TavernHub** é uma aplicação web projetada para ser o ponto de encontro de mesas de RPG. O objetivo é oferecer um dashboard onde jogadores e mestres sincronizam rolagens de dados e gerenciam personagens, unindo o poder do **Django** com a interatividade do **JavaScript**[cite: 3].

---

## 🛠️ Tecnologias Integradas

* **Backend:** Python 3.13+ & Django 6.0+[cite: 2, 5]
* **Frontend:** JavaScript Moderno (Vanilla), HTML5, CSS3 & Bootstrap 5
* **Gestão de Dados:** SQLite (Desenvolvimento) com suporte a Migrations (ORM Django)
* **Arquitetura:** MVC (Model-View-Controller) & **Publish-Subscribe (Django Signals)**[cite: 3, 4]
* **Qualidade:** Testes Automatizados (Django TestCase)[cite: 4]

---

## 🎯 Funcionalidades & Progresso

### Fase 1: O Tabuleiro Estático & Persistência (Concluída ✅)
- [x] Setup inicial do projeto Django e App Lobby[cite: 2].
- [x] Configuração de ambiente virtual (venv) e segurança (.gitignore)[cite: 2].
- [x] Interface com Widget de múltiplos dados (D4 a D100).
- [x] Conexão Front-End -> Back-End via Fetch API/JSON[cite: 5].
- [x] Log de Atividades com **Internacionalização (Brasília/UTC-3)**.

### Fase 2: O Coração do RPG - CRUD & Entidades (Concluída ✅)
- [x] **Gestão de Mesas (Entidade 1):** CRUD para criação e listagem de mesas.
- [x] **Gestão de Personagens (Entidade 2):** CRUD completo (Criar, Consultar, Editar e Excluir)[cite: 3].
- [x] **Sistema de Rolagens (Entidade 3):** Registro persistente com função de limpeza de log (Delete)[cite: 4].
- [x] **Integração de Entidades:** Vínculo real entre Personagem -> Mesa e Rolagem -> Personagem[cite: 3].
- [x] **Suíte de Testes:** Validação automatizada de rotas e integridade de dados[cite: 4].

### Fase 3: Lógica Avançada & Auditoria (Concluída ✅)
- [x] **Soft Delete de Personagens:** Implementação de exclusão lógica para manutenção de integridade[cite: 3].
- [x] **Paradigma Publish-Subscribe (Signals):** Monitoramento automático de críticos e logs de auditoria no terminal[cite: 3, 4].
- [x] **API com Filtros Dinâmicos:** Refinamento da leitura permitindo filtragem por tipo de dado via URL[cite: 3, 4].

### Fase 4: Inteligência de Dados & Segurança (Concluída ✅)
- [x] **Painel de Estatísticas (Aggregations):** Uso de `Avg`, `Count` e `Max` para processar médias de resultados e ranking de jogadores ativos diretamente no banco de dados[cite: 3, 6].
- [x] **Sistema de Rollback (Versionamento):** Implementação de edição auditável de rolagens. O sistema preserva o `resultado_anterior` e o motivo da alteração para transparência da mesa[cite: 3, 6].
- [x] **Mesa Protegida (Permissões):** Restrição de acesso baseada em perfis. Apenas o Mestre (Dono da Mesa) possui permissão para realizar Rollbacks ou gerenciar configurações críticas[cite: 3, 6].

### Fase 5: A Magia do Tempo Real (Próximos Passos 🚧)
- [ ] Sincronização de rolagens via WebSockets (Django Channels).
- [ ] Sistema de Iniciativa (Tracker) ordenável.
- [ ] Implementação de Django Messages para feedback visual de ações (UX).
- [ ] Integração de notas rápidas exportáveis para o Obsidian.

---

## 🚀 Como Executar o Projeto Localmente (Linux/VS Code)

Siga os passos abaixo para configurar e rodar o sistema:

1. **Clonar o repositório:**
   ```bash
   git clone <link-do-seu-repo>
   cd tavern-hub