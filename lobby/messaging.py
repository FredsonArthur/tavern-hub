import pika
import json

def publicar_rolagem(dados_rolagem):
    """
    Despacha o evento de rolagem de dado para o broker RabbitMQ.
    Cumpre o papel de 'Publisher' no requisito de Pub-Sub.
    """
    try:
        # 1. Conecta ao servidor local do RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # 2. Garante que a fila existe e é persistente (durable)
        channel.queue_declare(queue='cronicas_rolagem', durable=True)

        # 3. Converte o dicionário Python em uma string JSON
        payload = json.dumps(dados_rolagem)

        # 4. Publica a mensagem na fila de forma persistente
        channel.basic_publish(
            exchange='',
            routing_key='cronicas_rolagem',
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente em disco
            )
        )

        # 5. Fecha a conexão com segurança
        connection.close()
        print(f"📡 [RabbitMQ] Evento enviado com sucesso: {payload}")

    except Exception as e:
        # Registra o erro no log se o broker cair, mas não quebra o jogo do usuário
        print(f"⚠️ [RabbitMQ] Falha ao enviar evento: {e}")