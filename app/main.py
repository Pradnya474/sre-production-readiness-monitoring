import os
import time
import random
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = Flask(__name__)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
START_TIME = time.time()
READY = True

@app.before_request
def before_request():
    from flask import request, g
    g.start_time = time.time()

@app.after_request
def after_request(response):
    from flask import request, g
    endpoint = request.endpoint or "unknown"
    status = str(response.status_code)
    REQUESTS.labels(request.method, endpoint, status).inc()
    elapsed = time.time() - getattr(g, "start_time", time.time())
    LATENCY.labels(endpoint).observe(elapsed)
    return response

@app.get("/")
def index():
    return jsonify(service="sample-orders-api", status="running")

@app.get("/health")
def health():
    return jsonify(status="healthy", uptime_seconds=round(time.time() - START_TIME, 2)), 200

@app.get("/ready")
def ready():
    if not READY:
        return jsonify(status="not_ready"), 503
    return jsonify(status="ready"), 200

@app.get("/api/orders")
def orders():
    time.sleep(random.uniform(0.01, 0.08))
    return jsonify(orders=[{"id": 101, "status": "created"}, {"id": 102, "status": "shipped"}])

@app.get("/api/slow")
def slow():
    time.sleep(1.2)
    return jsonify(status="slow-response", simulated_delay_seconds=1.2)

@app.get("/api/fail")
def fail():
    return jsonify(error="simulated internal error", hint="Use this endpoint only for the local alerting exercise."), 500

@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
