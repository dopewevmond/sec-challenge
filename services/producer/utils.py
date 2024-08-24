from pika import BasicProperties


def generate_api_endpoints(
    base_url: str, total_results: int, results_per_page: int, other_params: dict = None
):
    endpoints = []
    if other_params is None:
        other_params = {}

    # Iterate through pagination
    for start_index in range(0, total_results, results_per_page):
        # Calculate the number of results on the current page
        current_results_per_page = min(results_per_page, total_results - start_index)

        # Build parameters for this endpoint
        params = {"startIndex": start_index, "resultsPerPage": current_results_per_page}
        params.update(other_params)

        # Create the query string and append to endpoints list
        query_string = dict_to_query_string(params)
        endpoints.append(f"{base_url}?{query_string}")

    return endpoints


def dict_to_query_string(d: dict):
    return "&".join(f"{key}={value}" for key, value in d.items())


def send_to_queue(channel, queue_name, message):
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
        properties=BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    print(f" [x] Sent {message} to {queue_name}")
