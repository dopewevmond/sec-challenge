FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    cron \
    python3 \
    python3-pip \
    curl

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

COPY wait_for_it.sh /usr/local/bin/wait_for_it.sh
RUN chmod +x /usr/local/bin/wait_for_it.sh
COPY run_producer.sh /usr/local/bin/run_producer.sh
RUN chmod +x /usr/local/bin/run_producer.sh

RUN echo '* * * * * /usr/local/bin/run_producer.sh >> /var/log/cron.log 2>&1' > /etc/cron.d/producer-cron \
    && chmod 0644 /etc/cron.d/producer-cron \
    && crontab /etc/cron.d/producer-cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]