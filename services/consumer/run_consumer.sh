#!/bin/bash

echo "Waiting for RabbitMQ to be available..."
/usr/local/bin/wait_for_it.sh rabbitmq:5672 --timeout=30 -- \
echo "RabbitMQ is up. Waiting for Redis to be available..." && \
/usr/local/bin/wait_for_it.sh redis:6379 --timeout=30 -- \
echo "Redis is up. Waiting for mongodb..." && \
/usr/local/bin/wait_for_it.sh mongodb:27017 --timeout=30 -- \
echo "Mongodb is up. Starting the consumer script..." && \
python3 /app/consumer.py
