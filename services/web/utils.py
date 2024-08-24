import pika

def send_to_queue(channel, queue_name, message):
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,
        ),
    )
    print(f" [x] Sent {message} to {queue_name}")