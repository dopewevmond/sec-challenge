#!/bin/bash

echo "Waiting for RabbitMQ to be available..."
/usr/local/bin/wait_for_it.sh rabbitmq:5672 --timeout=30 -- \
echo "RabbitMQ is up. Waiting for Redis to be available..." && \
/usr/local/bin/wait_for_it.sh redis:6379 --timeout=30 -- \
echo "Redis is up. Starting the producer script..." && \
python3 /app/producer.py
