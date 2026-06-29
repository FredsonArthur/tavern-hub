import pika
import json
import logging
import os

# Configuração de logger
logger = logging.getLogger(__name__)

# Lê configuração do ambiente ou usa padrão local
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'cronicas_rolagem')

def publicar_rolagem(dados_rolagem):
    """
    Despacha o evento de rolagem de dado para o broker RabbitMQ.
    """
    try:
        # Credenciais
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            connection_attempts=2,
            retry_delay=1
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Garante que a fila existe
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        # Serialização e publicação
        payload = json.dumps(dados_rolagem)
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=payload,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()
        logger.info(f"📡 [RabbitMQ] Evento enviado: {payload}")

    except pika.exceptions.AMQPConnectionError:
        logger.error("⚠️ [RabbitMQ] Conexão recusada. Verifique se o RabbitMQ está rodando.")
    except Exception as e:
        logger.error(f"⚠️ [RabbitMQ] Falha ao enviar evento: {e}")