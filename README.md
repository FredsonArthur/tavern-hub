# 🏰 TavernHub — O Lobby de Sessão Interativo para RPG

<p align="center">
  <img src="https://images.unsplash.com/photo-1519074069444-1ba4fff16411?q=80&w=1000&auto=format&fit=crop" alt="TavernHub Banner" width="100%" style="border-radius: 8px; max-height: 400px; object-fit: cover;">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-6.0+-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Node.js-20+-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" alt="RabbitMQ">
  <img src="https://img.shields.io/badge/OS-Fedora_Linux-3C6EB4?style=for-the-badge&logo=fedora&logoColor=white" alt="OS Fedora Linux">
</p>

O **TavernHub** é uma plataforma web de alta performance desenvolvida para atuar como o ponto de encontro virtual e centralizador de sessões de RPG de mesa. O sistema fornece um dashboard interativo em tempo real onde jogadores e mestres gerenciam fichas, moldam inventários complexos e realizam rolagens de dados auditáveis síncronas e assíncronas.

Sua infraestrutura de software adota padrões avançados de engenharia, unindo a robustez do ecossistema corporativo **Django** no back-end principal com um microsserviço assíncrono em **Node.js** alimentado por mensageria via **RabbitMQ**. O resultado é uma arquitetura distribuída, fracamente acoplada, resiliente a falhas e otimizada com cache de baixo nível.

---

## 🛠️ Especificações Técnicas e Arquitetura do Ecossistema

O ecossistema foi projetado dividindo responsabilidades de forma estrita entre os serviços para garantir isolamento de processos e consistência de dados:

### 💻 Stack Tecnológica Homologada
* **Back-end Core:** **Python 3.13+** e **Django 6.0+** utilizando o ORM nativo para mapeamento relacional, controle de concorrência e restrições de permissão.
* **Broker de Mensagens:** **RabbitMQ (AMQP)** atuando como a espinha dorsal de eventos assíncronos no paradigma **Publish-Subscribe (Pub-Sub)**[cite: 4].
* **Engine de Persistência Paralela (Store):** **Node.js 20+** rodando um consumidor nativo que captura streams de eventos da fila e escreve logs de auditoria em disco[cite: 4].
* **Front-end / UX:** **Vanilla JavaScript (ES6)** orientado a eventos com transporte assíncrono de objetos estruturados via **Fetch API / JSON**[cite: 4], integrados a uma interface customizada em modo escuro utilizando **Bootstrap 5**[cite: 4].
* **Camada de Cache:** Mecanismo de **Cache de Baixo Nível** em memória para blindagem de performance em consultas de agregação matemática.
* **Fuso Horário:** Sincronização internacional configurada para o fuso `America/Sao_Paulo` (Horário de Brasília)[cite: 4].
* **Ambiente de Desenvolvimento:** Sistema desenvolvido e testado nativamente sobre a distribuição **Fedora Linux**[cite: 4].

### 🏗️ Fluxo de Dados Distribuído (Pub-Sub-Store)
```text
  [ Jogador clica no d20 ]
             │
             ▼
    ┌────────────────┐
    │   Django App   │ ───► [ Persiste no SQLite / Invalida Cache ]
    └────────────────┘
             │
             │ (Publica payload JSON do evento via AMQP)
             ▼
    ┌────────────────┐
    │    RabbitMQ    │ [Fila Ativa: rolagens_dados]
    └────────────────┘
             │
             │ (Consome assincronamente sem onerar o HTTP)
             ▼
    ┌────────────────┐
    │  Worker Node   │ ───► [ Append em rolagens_store.json (Disco) ]
    └────────────────┘
```
🎯 Detalhes das Funcionalidades e Regras de Negócio👥 1. Módulo Relacional de Entidades (CRUDs Completos)Mesas de Jogo (Entidade Mestre): Centraliza as campanhas de RPG[cite: 4]. Possui relacionamento ForeignKey com o modelo User do Django para mapear o Mestre da mesa. A aplicação garante de forma automatizada que apenas o criador possua prerrogativas administrativas de edição sobre a mesa.  Fichas de Heróis (Entidade Personagem): Controla o ciclo de vida dos avatares dos jogadores[cite: 4]. Integra um mecanismo de Exclusão Lógica (Soft Delete) utilizando uma flag booleana ativo=True/False. Quando removido, o personagem fica oculto das listagens, mas seu histórico de jogo permanece intocado no banco de dados, protegendo estatísticas globais e logs de sessão.  Catálogo Global de Itens e Inventário (Many-to-Many): Engine de itens rica gerenciada via tabela associativa intermediária (ManyToManyField)[cite: 4]. Um item pode pertencer a vários heróis e um herói pode portar diversos itens em seu inventário de forma cumulativa[cite: 4].🔍 2. Mecanismo de Filtro Avançado CombinadoO painel de gerenciamento de personagens traz uma barra de busca multifator que intercepta requisições GET e monta dinamicamente consultas agregadas no banco de dados:  Busca Textual Dinâmica: Filtra registros por correspondência parcial ou total do nome digitado através da instrução ORM nome__icontains, garantindo que diferenças de caixa alta ou baixa não quebrem a pesquisa.  Filtro de Categoria Estrito: Executa a varredura exata de classes de jogo no banco com look-up classe__iexact.  Isolamento por Vínculo de Campanha: Permite buscar heróis pertencentes a uma ID de mesa específica ou caçar personagens sem grupo utilizando a cláusula de nulidade relacional mesa__isnull=True.  Preservação de Estado: Todos os inputs do formulário de filtro seguram o seu estado visível mesmo após a renderização da página, evitando que o usuário perda o contexto de busca atual.  📊 3. Inteligência de Dados, Cache e AuditoriaPainel de Análise (Aggregations): Computa em tempo de execução dados volumétricos e analíticos do servidor utilizando agregadores nativos da engine de banco do Django (Avg para médias de dados, Count para totalizadores e Max para recordes de jogadas).  Cache Computacional de Baixo Nível: Os resultados pesados gerados pelas agregações do painel são cacheados sob a chave painel_estatisticas_data com tempo de vida de 300 segundos. Para evitar inconsistência visual, qualquer nova inserção de rolagem ou alteração de estado no banco dispara uma instrução reativa de invalidação (cache.delete), forçando um recálculo sob demanda apenas quando estritamente necessário.  Sistema de Rollback Auditável: Se um dado cair da mesa ou houver divergência, o Mestre pode invocar o rollback de resultados[cite: 2, 4]. O sistema mantém a imutabilidade do histórico arquivando o dado anterior na coluna resultado_anterior, ativando o gatilho editado=True e bloqueando a transação caso uma justificativa textual detalhada não seja enviada pelo formulário.  Escopo de Segurança Hermético: Todas as operações sensíveis (como reverter rolagens e deletar dados) são validadas em nível de controlador via código Python, comparando o request.user com o mestre associado da mesa, devolvendo um HTTP 403 Forbidden imediato em caso de invasão ou requisição ilícita[cite: 2, 4].🗄️ Estrutura Arquitetural do Banco de DadosTabela: lobby_mesaCampoTipoDescriçãoidBigAutoField (PK)Identificador único sequencial da mesa.tituloCharField(200)Nome da mesa/campanha.data_criacaoDateTimeFieldRegistro cronológico da criação.mestre_idForeignKey (User)Usuário administrador responsável pela mesa.Tabela: lobby_personagemCampoTipoDescriçãoidBigAutoField (PK)Identificador único do personagem.nomeCharField(100)Nome do herói no jogo.racaCharField(50)Raça escolhida (Ex: Elfo, Anão).classeCharField(50)Classe de atuação (Ex: Mago, Guerreiro).nivelIntegerFieldNível de progressão do personagem.ativoBooleanFieldFlag controladora do Soft Delete (Padrão: True).usuario_idForeignKey (User)Jogador proprietário da ficha.mesa_idForeignKey (Mesa)Mesa de RPG na qual o personagem está inserido (Opcional).Tabela: lobby_itemCampoTipoDescriçãoidBigAutoField (PK)Identificador único do item no compêndio global.nomeCharField(100)Nome do equipamento (Ex: Espada Longa).raridadeCharField(50)Classificação (Comum, Raro, Lendário).ativoBooleanFieldFlag de controle de catálogo ativo.Tabela: lobby_rolagemCampoTipoDescriçãoidBigAutoField (PK)Código identificador do log do dado.jogador_nomeCharField(100)Nome legível exibido no feed de rolagens.tipo_dadoCharField(10)Tipo do poliedro acionado (D6, D20, D100).resultadoIntegerFieldValor atual computado no dado.resultado_anteriorIntegerFieldValor antigo guardado em caso de Rollback.editadoBooleanFieldIdentifica se o resultado foi alterado pelo Mestre (Padrão: False).motivo_edicaoTextFieldJustificativa preenchida para fins de auditoria técnica.data_horaDateTimeFieldTimestamp exato da jogada ajustado ao fuso regional.mesa_idForeignKey (Mesa)Contexto da campanha onde o dado foi lançado.personagem_idForeignKey (Personagem)Herói que executou a rolagem (Opcional).🚀 Instruções de Instalação e Execução (Fedora Linux)Siga os passos abaixo no terminal do seu Fedora para subir os serviços e rodar a aplicação:1. Clonar o Repositório e Preparar as Dependências do FedoraBash# Clone o projeto da taverna
git clone [https://github.com/SeuUsuario/tavern-hub.git](https://github.com/SeuUsuario/tavern-hub.git)
cd tavern-hub

# Instale os pacotes base de sistema necessários no Fedora
sudo dnf update -y
sudo dnf install -y python3-pip python3-devel gcc rabbitmq-server nodejs
2. Configurar e Inicializar o Broker RabbitMQBash# Ative e inicialize o serviço do RabbitMQ pelo systemd
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Verifique se o broker de mensageria está operacional e rodando com sucesso
sudo systemctl status rabbitmq-server
3. Configurar o Ambiente Python & DjangoBash# Crie e ative o ambiente isolado virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências core do ecossistema Python
pip install --upgrade pip
pip install -r requirements.txt

# Execute as migrações estruturais do banco de dados relacional
python manage.py migrate

# Crie um usuário mestre para gerenciar as primeiras mesas de jogo
python manage.py createsuperuser
4. Inicializar o Microsserviço de Persistência Paralela (Store)Abra uma nova aba de terminal, navegue até a pasta correspondente do projeto Node.js e ative o consumidor:Bash# Acesse o diretório do serviço Node
cd caminhos/para/seu/projeto_node/

# Instale as dependências de pacotes do npm (como o amqplib)
npm install

# Inicie o worker de escuta da fila AMQP
node consumidor.js
5. Rodar a Aplicação Web e a Suíte de TestesDe volta ao terminal principal com a venv ativa, rode o servidor web do Django:Bash# Inicie o servidor local integrado
python manage.py runserver
Acesse a aplicação pela URL padrão: http://127.0.0.1:8000/Para validar a integridade estrutural contra regressões ou falhas em tempo de execução, execute a suíte de testes:Bashpython manage.py test
