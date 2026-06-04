const amqp = require('amqplib');
const fs = require('fs');
const path = require('path');

const RABBITMQ_URL = 'amqp://localhost';
const QUEUE_NAME = 'cronicas_rolagem';
const STORE_FILE_PATH = path.join(__dirname, 'rolagens_store.json');

// Função auxiliar para persistir o dado no arquivo JSON (Store)
function salvarNaStore(novoEvento) {
    let historico = [];

    // 1. Se o arquivo já existir, lê o histórico atual
    if (fs.existsSync(STORE_FILE_PATH)) {
        try {
            const conteudo = fs.readFileSync(STORE_FILE_PATH, 'utf-8');
            historico = JSON.parse(conteudo || '[]');
        } catch (erro) {
            console.error("⚠️ Falha ao ler arquivo de store existente, resetando histórico:", erro.message);
        }
    }

    // 2. Adiciona o novo evento de rolagem ao array
    historico.push(novoEvento);

    // 3. Grava de volta no disco de forma síncrona para garantir consistência acid
    fs.writeFileSync(STORE_FILE_PATH, JSON.stringify(historico, null, 4), 'utf-8');
    console.log(`💾 [Store] Evento #${novoEvento.id} persistido com sucesso em rolagens_store.json`);
}

async function iniciarConsumidor() {
    try {
        const conexao = await amqp.connect(RABBITMQ_URL);
        const canal = await conexao.createChannel();

        await canal.assertQueue(QUEUE_NAME, { durable: true });

        console.log(`\x1b[33m%s\x1b[0m`, `[📜 Microsserviço Pub-Sub-Store]`);
        console.log(`📡 Aguardando rolagens e persistindo dados... Pressione CTRL+C para sair\n`);

        canal.consume(QUEUE_NAME, (mensagem) => {
            if (mensagem !== null) {
                const conteudo = JSON.parse(mensagem.content.toString());
                
                console.log(`\x1b[32m%s\x1b[0m`, `🎲 [DADO RECEBIDO]`);
                console.log(`👤 Jogador:  ${conteudo.jogador_nome}`);
                console.log(`🎲 Dado:     ${conteudo.tipo_dado} | Resultado: ${conteudo.resultado}`);
                
                // 🔥 Executa a Persistência (Requisito v)
                salvarNaStore(conteudo);
                
                console.log(`-----------------------------------------`);

                canal.ack(mensagem);
            }
        });

    } catch (erro) {
        console.error("❌ Erro crítico no microsserviço Store:", erro);
    }
}

iniciarConsumidor();