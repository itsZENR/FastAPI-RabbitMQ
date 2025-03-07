import os
import pika
from fastapi import FastAPI

app = FastAPI()

# Читаем переменные окружения (из docker-compose или напрямую)
RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "guest")
RABBIT_PASS = os.getenv("RABBIT_PASS", "guest")

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
params = pika.ConnectionParameters(
    host=RABBIT_HOST, port=RABBIT_PORT, credentials=credentials
)

connection = None
channel = None


def get_connection_and_channel():
    global connection, channel

    # Если соединения ещё нет или оно закрыто – создаём заново
    if not connection or connection.is_closed:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue="my_queue", durable=True)

    # Если канал закрыт – пересоздаём его
    if not channel or channel.is_closed:
        channel = connection.channel()
        channel.queue_declare(queue="my_queue", durable=True)

    return connection, channel


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/send")
def send_message(msg: str):
    try:
        _, ch = get_connection_and_channel()
        ch.basic_publish(exchange="", routing_key="my_queue", body=msg)
        return {"status": "Message sent!", "msg": msg}
    except pika.exceptions.StreamLostError:
        # Попытаемся пересоздать соединение/канал и отправить снова
        time.sleep(1)  # маленькая пауза
        _, ch = get_connection_and_channel()
        ch.basic_publish(exchange="", routing_key="my_queue", body=msg)
        return {"status": "Message re-sent after reconnection", "msg": msg}
