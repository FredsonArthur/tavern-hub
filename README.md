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
- [x] **Gestão de Mesas:** CRUD para criação e listagem de mesas de jogo.
- [x] **Gestão de Personagens:** CRUD completo (Criar, Consultar, Editar e Excluir).
- [x] **Sistema de Rolagens:** Registro persistente com função de limpeza de log.
- [x] **Integração de Entidades:** Vínculo real entre Personagem -> Mesa e Rolagem -> Personagem.

### Fase 3: Lógica Avançada & Auditoria (Concluída ✅)
- [x] **Soft Delete de Personagens:** Implementação de exclusão lógica para manutenção de integridade.
- [x] **Paradigma Publish-Subscribe (Signals):** Monitoramento automático de críticos e logs de auditoria no terminal.
- [x] **API com Filtros Dinâmicos:** Refinamento da leitura permitindo filtragem por tipo de dado via URL.

### Fase 4: Inteligência de Dados & Segurança (Concluída ✅)
- [x] **Painel de Estatísticas (Aggregations):** Uso de `Avg`, `Count` e `Max` para processar médias e ranking diretamente no banco.
- [x] **Sistema de Rollback (Versionamento):** Edição auditável de rolagens preservando o `resultado_anterior`.
- [x] **Mesa Protegida (Permissões):** Acesso restrito. Apenas o Mestre possui permissão para Rollbacks e gestão crítica.

### Fase 5: Expansão de Inventário, UX & Estabilidade (Concluída ✅)
- [x] **Gestão de Inventário (Many-to-Many):** Entidade `Item` que permite personagens possuírem múltiplos equipamentos.
- [x] **Sinais de Inteligência:** Detecção automática de "Maré de Azar" (3 falhas seguidas) e alertas de "Riqueza".
- [x] **Feedback Visual (Django Messages):** Alertas dinâmicos de sucesso, erro e avisos integrados à interface.
- [x] **Navegação Consolidada:** Sistema de herança de templates e links dinâmicos para inventário no dashboard.
- [x] **Suíte de Testes:** Validação automatizada de segurança, integridade e fluxos principais.

---

## 🚀 Como Executar o Projeto Localmente

1. **Clonar o repositório:**
   ```bash
   git clone <link-do-seu-repo>
   cd tavern-hub