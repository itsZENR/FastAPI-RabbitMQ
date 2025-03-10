import os
import pika

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "guest")
RABBIT_PASS = os.getenv("RABBIT_PASS", "guest")

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
parameters = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, credentials=credentials)
print("Starting consumer script...")
connection = pika.BlockingConnection(parameters)
print("Connection successful, creating channel...")
channel = connection.channel()

channel.queue_declare(queue='my_queue', durable=True)

print(" [*] Waiting for messages. To exit press CTRL+C")

def callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Received: {message}", flush=True)
    # Здесь любая логика обработки
    # ...
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='my_queue', on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
