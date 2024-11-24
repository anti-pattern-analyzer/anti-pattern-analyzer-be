import requests
from app.core.database import trace_collection


def fetch_traces(service_name: str):
    url = f"http://localhost:16686/api/traces?service={service_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def fetch_and_store_traces(service_name: str):
    traces = fetch_traces(service_name)
    for trace in traces:
        trace_collection.insert_one(trace)
    return traces
