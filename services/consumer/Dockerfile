FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  curl

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

COPY wait_for_it.sh /usr/local/bin/wait_for_it.sh
RUN chmod +x /usr/local/bin/wait_for_it.sh
COPY run_consumer.sh /usr/local/bin/run_consumer.sh
RUN chmod +x /usr/local/bin/run_consumer.sh

CMD ["/usr/local/bin/run_consumer.sh"]