---
tags:
  - index
updated: 2026-04-04T10:00:00
id: 01M6K000000000000000000001
created: 2026-01-01T09:00:00
---
# Signalwatch

A Prometheus and Grafana stack monitoring my homelab machines — [[PuddleJumper]], [[LordByron]], and [[Bramble]]. Real-time dashboards and alerting for disk, CPU, and tailnet health.

## Dashboards & Alerts
- [[Signalwatch Dashboards]] — the two Grafana views (fleet overview and per-host).
- [[Signalwatch Alert Rules]] — thresholds and rule definitions.

## Operations
- [[Signalwatch False Positives]] — tuning to reduce noise during maintenance.
- [[Prometheus Retention Tuning]] — disk management after a fill event.
- [[Grafana Provisioning as Code]] — dashboards as YAML in git.
- [[Node Exporter Setup]] — systemd unit on each host.
