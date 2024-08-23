FROM python:3.9-slim
WORKDIR /app
COPY pika_worker.py /app
RUN pip install --no-cache-dir pika pymongo
CMD ["python", "./pika_worker.py"]
