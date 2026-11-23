# SRE Production Readiness Lab

A portfolio-ready Site Reliability Engineering (SRE) project that demonstrates:
- A small Python/Flask service with health/readiness endpoints and Prometheus metrics
- Docker containerization and Docker Compose orchestration
- Prometheus scraping and alert rules
- Grafana provisioning with a starter dashboard
- Synthetic load and controlled failure exercises
- Incident runbooks, SLI/SLO definitions, and postmortem template

> This is a local learning lab, not a real production system. Run it locally and only describe the parts you have actually implemented and tested.

## Architecture

Client / curl
   |
   v
Flask API (Docker container) ----> Prometheus metrics at /metrics
   |                                      |
   +-- /health                            v
   +-- /ready                         Prometheus
   +-- /api/orders                         |
                                          v
                                       Grafana

## Requirements
- Docker Engine and Docker Compose plugin
- Optional: Python 3.11+ if running the API outside Docker

## Start the stack

```bash
docker compose up --build -d
docker compose ps
```

Open:
- API: http://localhost:8000
- Health: http://localhost:8000/health
- Readiness: http://localhost:8000/ready
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (username `admin`, password `admin`)

Change the Grafana password after first login if you keep this running.

## Smoke tests

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
curl -i http://localhost:8000/api/orders
curl -s http://localhost:8000/metrics | head
```

Generate traffic:

```bash
python scripts/load_test.py --url http://localhost:8000 --requests 100 --concurrency 5
```

Trigger a controlled application error to exercise the error-rate alert:

```bash
for i in $(seq 1 20); do curl -s -o /dev/null http://localhost:8000/api/fail; done
```

Check Prometheus at http://localhost:9090/alerts and Grafana dashboards.

## SRE exercises

1. **Service health:** stop the API container with `docker compose stop api`. Observe target health in Prometheus and check `/health`. Restore it using `docker compose start api`.
2. **Error rate:** call `/api/fail` repeatedly. Inspect `http_requests_total` and the `HighHTTPErrorRate` alert.
3. **Latency:** generate normal traffic and inspect request latency histogram metrics.
4. **Capacity:** run the load test with increasing concurrency. Observe CPU/memory using `docker stats`.
5. **Recovery:** restart the service and verify health, readiness, and alert recovery.

## SLI / SLO examples

These are practice targets, not measured guarantees:
- Availability SLI: successful `/health` probes / total `/health` probes.
- Request success SLI: non-5xx requests / all requests.
- Latency SLI: proportion of requests completed in <= 500 ms.
- Example monthly availability SLO: 99.5%.
- Example latency SLO: 95% of requests under 500 ms.

## Useful PromQL

```promql
sum(rate(http_requests_total[5m]))
```

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
clamp_min(sum(rate(http_requests_total[5m])), 1)
```

```promql
histogram_quantile(
  0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

## Troubleshooting commands

```bash
docker compose logs -f api
docker compose logs -f prometheus
docker compose logs -f grafana
docker stats
docker compose config
docker compose down
```

## Interview explanation

"I built a local SRE observability lab for a containerized Flask service. I exposed health and readiness endpoints, instrumented request count and latency metrics, scraped those metrics with Prometheus, and provisioned a Grafana dashboard. I added alert rules for service availability and elevated HTTP 5xx responses. I also documented SLI/SLO examples, operational runbooks, and failure-injection exercises so I could practice detection, diagnosis, recovery, and post-incident review."

## Resume bullets (use only after completing the work)

- Built a Dockerized REST service with health/readiness probes and Prometheus instrumentation.
- Configured Prometheus scraping, alert rules, and Grafana dashboard provisioning for service observability.
- Practiced incident scenarios including service unavailability and elevated HTTP 5xx errors; documented investigation and recovery steps.
- Defined example SLIs/SLOs and created an incident runbook and postmortem template.

## Cleanup

```bash
docker compose down -v
```
