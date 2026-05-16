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
- [x] Interface com Widget de múltiplos dados (D4 a D100).
- [x] Conexão Front-End -> Back-End via Fetch API/JSON.
- [x] Log de Atividades com **Internacionalização (Brasília/UTC-3)**.

### Fase 2: O Coração do RPG - CRUD & Entidades (Concluída ✅)
- [x] **Gestão de Mesas:** CRUD para criação e listagem de mesas de jogo.
- [x] **Gestão de Personagens:** CRUD completo (Criar, Consultar, Editar e Excluir).
- [x] **Integração de Entidades:** Vinculação dinâmica de personagens a mesas ativas.

### Fase 3: Arquitetura Assíncrona & Lógica de Jogo (Concluída ✅)
- [x] **Soft Delete de Personagens:** Implementação de exclusão lógica para manutenção de integridade.
- [x] **Paradigma Publish-Subscribe (Signals):** Monitoramento automático de críticos e logs de auditoria no terminal.
- [x] **API com Filtros Dinâmicos:** Refinamento da leitura permitindo filtragem por tipo de dado via URL.

### Fase 4: Inteligência de Dados & Segurança (Concluída ✅)
- [x] **Painel de Estatísticas (Aggregations):** Uso de `Avg`, `Count` e `Max` para processar médias e ranking.
- [x] **Sistema de Rollback (Versionamento):** Edição auditável de rolagens preservando o `resultado_anterior`.
- [x] **Mesa Protegida (Permissões):** Acesso restrito. Apenas o Mestre possui permissão para Rollbacks.

### Fase 5: Expansão de Inventário, UX & Estabilidade (Concluída ✅)
- [x] **Gestão de Inventário (Many-to-Many):** Entidade `Item` que permite personagens possuírem múltiplos equipamentos.
- [x] **Biblioteca Global de Itens:** Interface dedicada para forjar e listar itens disponíveis no mundo.
- [x] **Sinais de Inteligência:** Detecção automática de "Maré de Azar" (3 falhas seguidas) e alertas de "Riqueza".
- [x] **Feedback Visual (Django Messages):** Alertas dinâmicos de sucesso, erro e avisos integrados à interface.
- [x] **Navegação Consolidada:** Sistema de herança de templates e links dinâmicos para inventário no painel de personagens.
- [x] **Suite de Testes Automatizados:** Implementação de testes de Unidade, Integração, M2M Signals, Proteção de Views e Regressão de Soft Delete com 100% de aprovação.

---

## 🧪 Como Executar os Testes

Para garantir que nenhuma alteração quebre as regras de negócio core da taverna, execute a suite de testes integrada:

```bash
python manage.py test