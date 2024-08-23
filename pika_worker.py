import pika
import os
import time
from pymongo import MongoClient

rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbit')
write_queue_name = os.environ.get('WRITE_QUEUE_NAME', 'write_cve')
mongo_host = os.environ.get('MONGO_DB_HOST', 'mongodb')
mongo_username = os.environ.get('MONGODB_USERNAME', 'mongodb')
mongo_password = os.environ.get('MONGO_DB_PASSWORD', 'mongodb')
mongo_dbname = os.environ.get('MONGODB_DBNAME', 'mongodb')

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    # Add your task processing logic here
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    mongo_client = MongoClient(mongo_host, 27017, username=mongo_username, password=mongo_password)
    db = mongo_client[mongo_dbname]
    print(db)

    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue=write_queue_name, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=write_queue_name, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()