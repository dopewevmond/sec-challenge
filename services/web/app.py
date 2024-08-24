from flask import Flask, render_template, request, url_for, redirect
import os
import pika
import uuid
from utils import send_to_queue
import json
import redis

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_read_db_data_queue = os.getenv("RABBITMQ_CVE_READ_QUEUE", "read__cve_entry")
redis_host = os.getenv("REDIS_HOST", "localhost")

r = redis.Redis(host=redis_host, port=6379)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


@app.route("/cves", methods=["GET"])
def get_cves():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_read_db_data_queue, durable=True)

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))
    request_id = request.args.get("request_id")

    params = {"limit": limit, "offset": offset, "request_id": request_id}

    if request_id is not None and r.get(f"EXISTS_{request_id}") is not None:
        deserialized = r.get(request_id)
        if deserialized is not None:
            data = json.loads(deserialized)
            data["ready"] = True
            print(json.dumps(data, indent=2))
            return render_template("cve.html", data=data)
        else:
            return render_template("cve.html", data={"ready": False})

    request_id = str(uuid.uuid4())
    params["request_id"] = request_id

    r.set(f"EXISTS_{request_id}", "True", ex=86400)

    send_to_queue(
        channel=channel,
        queue_name=rabbitmq_read_db_data_queue,
        message=json.dumps(params),
    )
    connection.close()
    stateful_url = url_for("get_cves", **params)
    return redirect(stateful_url)
