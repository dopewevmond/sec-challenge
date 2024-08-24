import pika
import os
import sys
from dotenv import load_dotenv
load_dotenv()

rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
rabbitmq_cve_entries_queue = os.environ.get(
    "RABBITMQ_CVE_ENTRIES_QUEUE", "process__cve_entries_queue"
)


def callback(ch, method, properties, body):
    print(properties)
    print(f" [x] Done - {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue=rabbitmq_cve_entries_queue, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=rabbitmq_cve_entries_queue, on_message_callback=callback
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('stopping the consumer')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
