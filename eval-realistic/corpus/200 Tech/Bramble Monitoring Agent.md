---
updated: 2026-07-20T11:29:00
id: 01M6B00000000000000000000E
created: 2026-06-20T10:13:00
---
# Bramble Monitoring Agent

Installing a lightweight resource monitor on the Bramble VPS itself.

## Rationale
Bramble hosts the log aggregation and Caddy reverse proxy for my homelab. If Bramble goes down, I lose visibility and external access. Running a local monitor lets me see CPU/memory/disk trends and catch resource exhaustion before it becomes a crisis.

## Setup
I deployed node-exporter as a systemd service that collects metrics and exposes them on localhost:9100. The metrics scraper on my home network pulls these every 60 seconds. I set alerts for disk usage >80%, sustained CPU >70%, and memory >85%.
