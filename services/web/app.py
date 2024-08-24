from flask import Flask, render_template, request, url_for, redirect
import os
import pika
import uuid
from utils import send_to_queue
import json

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_read_db_data_queue = os.getenv("RABBITMQ_CVE_READ_QUEUE", "read__cve_entry")


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

    # check if key in redis with prefix of EXISTS_<request_id> exists so we know that the worker is about to process it
    if request_id is not None: # or redis EXISTS_<request_id> key doesnt exist
        pass
        # lets check redis if it's ready
        # if it is
            # let's serialize it and return it and delete from redis
            # delete the key in redix with prefix of EXISTS_<request_id> since it has been processed

        # if it's not ready, let's return same link that says please try again in a few seconds
        # return
        return render_template("cve.html", data={"data": "data"})

    request_id = str(uuid.uuid4())
    params["request_id"] = request_id
    
    
    # set a key in redix with prefix of EXISTS_<request_id> so we know it's about to be processed

    send_to_queue(
        channel=channel,
        queue_name=rabbitmq_read_db_data_queue,
        message=json.dumps(params),
    )
    connection.close()
    stateful_url = url_for("get_cves", **params)
    return redirect(stateful_url)
