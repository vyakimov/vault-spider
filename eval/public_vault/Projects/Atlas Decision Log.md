---
id: 01JEV000000000000000000004
title: Atlas Decision Log
type: decision-log
created: 2024-01-18T11:00:00Z
updated: 2025-03-01T09:45:00Z
tags: [atlas, decisions, architecture]
---
# Atlas Decision Log

## 2024-01-18 — HTTPS batching instead of continuous MQTT

Atlas uses compressed HTTPS batches from Cedar to Harbor. The field connection disappears for
hours at a time, so a local durable queue and explicit batch acknowledgements are easier to reason
about than a continuously connected session.

## 2024-04-09 — PostgreSQL for queryable readings

PostgreSQL was selected because the dataset is relational, modest in scale, and queried by time,
station, and sensor. Original compressed batches remain in object storage for replay.

## 2025-02-20 — Retention policy

Raw readings remain queryable for 90 days. Hourly and daily summaries are retained indefinitely.
This keeps the operational database small while preserving long-term trends.

## 2025-03-01 — No raw payloads in telemetry

Logs and traces may contain sensor IDs, counts, durations, and reason codes, but not raw batches.
This allowlist makes observability useful without duplicating the dataset in a logging system.

