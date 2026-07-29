---
updated: 2026-01-16T13:41:00
id: 01M6E00000000000000000000R
created: 2026-07-14T10:49:00
---
`sum(rate(http_requests_total[5m])) by (handler)` shows request rate per handler; `topk(5, node_memory_MemFree_bytes)` gets 5 nodes with most free memory. `increase(errors_total[1h])` counts errors in last hour; combine with `on()` for joins: `rate(requests[5m]) / ignoring(le) rate(latency_bucket[5m])`. Use Grafana or Prometheus UI to test queries.
