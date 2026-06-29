const amqp = require('amqplib');
const fs = require('fs');
const path = require('path');

// Lê configuração do ambiente ou usa padrão local
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@rabbitmq:5672';
const QUEUE_NAME = process.env.RABBITMQ_QUEUE || 'cronicas_rolagem';
const STORE_FILE_PATH = path.join(__dirname, 'rolagens_store.json');

function salvarNaStore(novoEvento) {
    let historico = [];

    if (fs.existsSync(STORE_FILE_PATH)) {
        try {
            const conteudo = fs.readFileSync(STORE_FILE_PATH, 'utf-8');
            historico = JSON.parse(conteudo || '[]');
        } catch (erro) {
            console.error("⚠️ Falha ao ler arquivo de store:", erro.message);
        }
    }

    historico.push(novoEvento);
    fs.writeFileSync(STORE_FILE_PATH, JSON.stringify(historico, null, 4), 'utf-8');
    console.log(`💾 [Store] Evento #${novoEvento.id} persistido`);
}

async function iniciarConsumidor() {
    try {
        const conexao = await amqp.connect(RABBITMQ_URL);
        const canal = await conexao.createChannel();
        await canal.assertQueue(QUEUE_NAME, { durable: true });

        console.log(`\x1b[33m%s\x1b[0m`, `[📜 Microsserviço Pub-Sub-Store]`);
        console.log(`📡 Conectado ao RabbitMQ em: ${RABBITMQ_URL}`);
        console.log(`📡 Aguardando rolagens na fila: ${QUEUE_NAME}\n`);

        canal.consume(QUEUE_NAME, (mensagem) => {
            if (mensagem !== null) {
                const conteudo = JSON.parse(mensagem.content.toString());

                console.log(`\x1b[32m%s\x1b[0m`, `🎲 [DADO RECEBIDO]`);
                console.log(`👤 Jogador:  ${conteudo.jogador_nome}`);
                console.log(`🎲 Dado:     ${conteudo.tipo_dado} | Resultado: ${conteudo.resultado}`);

                salvarNaStore(conteudo);
                console.log(`-----------------------------------------`);
                canal.ack(mensagem);
            }
        });

    } catch (erro) {
        console.error("❌ Erro crítico no microsserviço:", erro.message);
        console.error("Verifique se o RabbitMQ está rodando e a URL está correta.");
        process.exit(1);
    }
}

iniciarConsumidor();
