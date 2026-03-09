import pika
import threading
import time
import random

# Параметры подключения (адаптируйте, если не дефолт)
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
QUEUE_NAME = 'my_queue'  # имя очереди

def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    ))

# ── ПРОИЗВОДИТЕЛЬ ────────────────────────────────
def producer(name):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)  # создаём очередь, если нет

    for i in range(1, 11):
        item = f"{name} → {i:02d}"
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=item)
        print(f"  {item:18}  (отправлено)")
        time.sleep(4.0)

    # сигнал завершения для всех consumers
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body='STOP')
    connection.close()

# ── ПОТРЕБИТЕЛЬ ──────────────────────────────────
def consumer(name, stop_event):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        item = body.decode()
        if item == 'STOP':
            print(f"{name}: Получен сигнал STOP")
            stop_event.set()  # сигнал для завершения
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"                     ← {item:18}")
        time.sleep(5.0)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # подтверждаем обработку

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print(f"{name}: Запущен, жду сообщений...")
    channel.start_consuming()

# ── ЗАПУСК ───────────────────────────────────────
if __name__ == "__main__":
    # Для graceful shutdown consumers
    stop_events = []

    producers = []
    for i in range(2):
        t = threading.Thread(target=producer, args=(f"P{i+1}",))
        producers.append(t)
        t.start()

    consumers = []
    for i in range(3):
        stop_event = threading.Event()
        stop_events.append(stop_event)
        t = threading.Thread(target=consumer, args=(f"C{i+1}", stop_event), daemon=True)
        consumers.append(t)
        t.start()

    # Ждём завершения producers
    for p in producers:
        p.join()

    # Ждём, пока consumers обработают всё (через STOP)
    for stop_event in stop_events:
        stop_event.wait()  # ждём сигнала от каждого consumer
