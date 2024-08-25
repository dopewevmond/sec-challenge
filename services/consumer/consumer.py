import pika
import os
import sys
import json
import requests
import time
from data_writer import DataWriter
from dotenv import load_dotenv
import redis

load_dotenv()

writer = DataWriter()

rabbitmq_host = 'rabbitmq'
redis_host = 'redis'
rabbitmq_cve_entries_queue = 'cve'
# rabbitmq_cve_history_queue = 'cve_history'
rabbitmq_read_db_data_queue = 'read_cve'

r = redis.Redis(host=redis_host, port=6379)


def save_cve_callback(ch, method, properties, body):
    try:
        url = body.decode()
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                writer.save_cve(data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(f" [x] CVE API - Done processing URL: {url}")
            except json.JSONDecodeError:
                print(f"Error: Received invalid JSON from {url}")
                ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            print(f"Error: Received status code {response.status_code} from {url}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    except requests.exceptions.RequestException as e:
        print(f"Error requesting {url}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

    # delaying the next request to prevent rate limiting
    time.sleep(5)


# def save_cve_history_callback(ch, method, properties, body):
#     try:
#         url = body.decode()
#         response = requests.get(url)

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 writer.save_cve_history(data)
#                 ch.basic_ack(delivery_tag=method.delivery_tag)
#                 print(f" [x] CVE HISTORY API - Done processing URL: {url}")
#             except json.JSONDecodeError:
#                 print(f"Error: Received invalid JSON from {url}")
#                 ch.basic_nack(delivery_tag=method.delivery_tag)
#         else:
#             print(f"Error: Received status code {response.status_code} from {url}")
#             ch.basic_nack(delivery_tag=method.delivery_tag)

#     except requests.exceptions.RequestException as e:
#         print(f"Error requesting {url}: {e}")
#         ch.basic_nack(delivery_tag=method.delivery_tag)
#     time.sleep(5)


def write_db_data_to_redis(ch, method, properties, body):
    try:
        unserialized_params = body.decode()
        params = json.loads(unserialized_params)
        data = writer.fetch_cve_records(offset=params["offset"], limit=params["limit"])
        r.set(params["request_id"], json.dumps(data), ex=86400)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f" [x] API Response written to Redis - {params['request_id']}")
    except Exception as e:
        print(f"Error writing response to redis: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue=rabbitmq_read_db_data_queue, durable=True)
    channel.queue_declare(queue=rabbitmq_cve_entries_queue, durable=True)
    # channel.queue_declare(queue=rabbitmq_cve_history_queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=rabbitmq_read_db_data_queue, on_message_callback=write_db_data_to_redis
    )
    channel.basic_consume(
        queue=rabbitmq_cve_entries_queue, on_message_callback=save_cve_callback
    )
    # channel.basic_consume(
    #     queue=rabbitmq_cve_history_queue, on_message_callback=save_cve_history_callback
    # )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopping the consumer")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
