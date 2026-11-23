# Incident Runbook: Sample Orders API

## 1. Triage
1. Confirm alert and affected service.
2. Check `docker compose ps`.
3. Check `curl -i http://localhost:8000/health`.
4. Check Prometheus target status at `http://localhost:9090/targets`.
5. Review `docker compose logs --tail=200 api`.

## 2. API unavailable
- Check container state: `docker compose ps api`
- Inspect logs: `docker compose logs --tail=200 api`
- Check port binding: `docker compose port api 8000`
- Recovery for this lab: `docker compose up -d api`
- Verify `/health`, `/ready`, and Prometheus target.

## 3. Elevated HTTP 5xx
- Query `sum(rate(http_requests_total{status=~"5.."}[5m]))`.
- Identify the endpoint in logs and metrics.
- For this lab, `/api/fail` intentionally returns 500.
- Stop the test traffic and confirm the error rate falls.
- Record start/end time, impact, cause, and remediation.

## 4. Escalation
In a real environment, follow the organization's severity matrix, on-call policy, access controls, and change approval process. Do not restart or roll back production services without authorization.

## 5. Closure
- Confirm service health and alert recovery.
- Communicate impact and resolution.
- Create a problem record for recurring issues.
- Add preventive actions and owners.
