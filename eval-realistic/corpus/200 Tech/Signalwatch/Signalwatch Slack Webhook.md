---
updated: 2026-02-01T11:00:00
id: 01M6K000000000000000000008
created: 2026-01-01T10:00:00
---
# Signalwatch Slack Webhook

I route critical alerts from the monitoring stack to Signal notifications so I catch them on my phone instead of drifting into Grafana every hour.

## Setup
The Signalwatch agent runs a listener on the tailnet that accepts webhook POST requests. Alerts from Prometheus are configured to forward high-severity incidents (disk full, service down, replication lag) to this endpoint, which then sends a Signal message to my number. Latency is under 2s, which is good enough for ops.

## Tradeoffs
I initially tried Pushbullet for this, but prefer Signal for the encryption layer. The webhook payload gets hashed to prevent accidental leaks. Acknowledged alerts are logged but don't fire again within 30 minutes to reduce noise.
