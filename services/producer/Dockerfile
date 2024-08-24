FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    cron \
    python3 \
    python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN echo '*/2 * * * * python3 /app/producer.py >> /var/log/cron.log 2>&1' > /etc/cron.d/producer-cron \
    && chmod 0644 /etc/cron.d/producer-cron \
    && crontab /etc/cron.d/producer-cron
RUN touch /var/log/cron.log
CMD ["cron", "-f"]