import os
from datetime import datetime
import redis
import requests
import pika
from utils import generate_api_endpoints, send_to_queue
from dotenv import load_dotenv
load_dotenv()

redis_host = os.getenv("REDIS_HOST", "localhost")
rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
redis_cve_last_fetched_key = os.getenv("REDIS_LAST_FETCHED_KEY", "LAST_FETCH_CVE")
rabbitmq_cve_queue = os.getenv("RABBITMQ_CVE_ENTRIES_QUEUE", "process__cve_entries_queue")
rabbitmq_history_queue = os.getenv("RABBITMQ_CVE_HISTORY_QUEUE", "process__cve_history_queue")

CVE_API_BASEURL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CVE_HISTORY_API_BASEURL = "https://services.nvd.nist.gov/rest/json/cvehistory/2.0"
NUM_RESULTS_TO_PROCESS_IN_CYCLE = 100

now = datetime.now()
fts = now.strftime("%Y-%m-%dT%H:%M:%S")
formatted_timestamp = f"{fts}.{now.microsecond // 1000:03}"
# print(f"[x] Current date and time is {formatted_timestamp}")

# services
r = redis.Redis(host=redis_host, port=6379)
last_fetch_cve = r.get(redis_cve_last_fetched_key)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_cve_queue, durable=True)
channel.queue_declare(queue=rabbitmq_history_queue, durable=True)

# for CVE API
cve_api_endpoint = f"{CVE_API_BASEURL}?resultsPerPage=1"
if last_fetch_cve is not None:
    cve_api_endpoint += (
        f"&pubStartDate={last_fetch_cve.decode()}&pubEndDate={formatted_timestamp}"
    )
print(f"cve_api_endpoint: {cve_api_endpoint}")
cve_api_req = requests.get(cve_api_endpoint)
cve_api_response = cve_api_req.json()
total_cve_entries, cve_entries_timestamp = (
    cve_api_response["totalResults"],
    cve_api_response["timestamp"],
)
cve_params = {}
if last_fetch_cve:
    cve_params["pubStartDate"] = last_fetch_cve.decode()
    cve_params["pubEndDate"] = formatted_timestamp
cve_api_consumer_endpoints = generate_api_endpoints(
    base_url=CVE_API_BASEURL,
    total_results=total_cve_entries,
    results_per_page=NUM_RESULTS_TO_PROCESS_IN_CYCLE,
    other_params=cve_params,
)
print("cve_api_consumer_endpoints: ")
for endpoint in cve_api_consumer_endpoints:
    send_to_queue(channel=channel, queue_name=rabbitmq_cve_queue, message=endpoint)
print("\n")


# for CVE History API
history_api_endpoint = f"{CVE_HISTORY_API_BASEURL}?resultsPerPage=1"
if last_fetch_cve is not None:
    history_api_endpoint += f"&changeStartDate={last_fetch_cve.decode()}&changeEndDate={formatted_timestamp}"
print(f"history_api_endpoint: {history_api_endpoint}")
history_api_req = requests.get(history_api_endpoint)
history_api_response = history_api_req.json()
total_history_api_entries, history_api_entries_timestamp = (
    history_api_response["totalResults"],
    history_api_response["timestamp"],
)
history_params = {}
if last_fetch_cve:
    history_params["changeStartDate"] = last_fetch_cve.decode()
    history_params["changeEndDate"] = formatted_timestamp
history_api_consumer_endpoints = generate_api_endpoints(
    base_url=CVE_HISTORY_API_BASEURL,
    total_results=total_history_api_entries,
    results_per_page=NUM_RESULTS_TO_PROCESS_IN_CYCLE,
    other_params=history_params,
)
print("history_api_consumer_endpoints: ")
for endpoint in history_api_consumer_endpoints:
    send_to_queue(channel=channel, queue_name=rabbitmq_history_queue, message=endpoint)
print("\n")

# setting timestamp in redis so we can fetch only new changes/additions on subsequent runs of cron job
r.set(redis_cve_last_fetched_key, formatted_timestamp)
