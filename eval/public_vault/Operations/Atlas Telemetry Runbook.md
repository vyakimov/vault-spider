---
id: 01JEV000000000000000000007
title: Atlas Telemetry Runbook
aliases: [Telemetry Runbook]
type: runbook
created: 2024-03-08T08:00:00Z
updated: 2025-02-18T11:00:00Z
tags: [atlas, operations, telemetry]
---
# Atlas Telemetry Runbook

## Alert thresholds

- Cedar queue backlog above 500 readings for 20 minutes: warning.
- No accepted Harbor batch for 15 minutes: warning.
- Gateway disk use above 80 percent: warning; above 90 percent: critical.
- Sensor clock offset above five minutes: warning.

## Triage order

Check whether Cedar is still collecting locally, then check the WireGuard tunnel, then Harbor's
`/healthz` endpoint. If collection continues, preserve the queue and avoid a factory reset. If disk
pressure is high, remove rotated logs before restarting services.

## Successful recovery

Recovery is complete when the queue backlog returns to zero, Harbor accepts a synthetic batch, and
the dashboard's newest timestamp is less than ten minutes old.

