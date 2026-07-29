---
tags:
  - homelab
updated: 2026-01-06T10:22:00
id: 01M6K000000000000000000003
created: 2026-03-03T09:14:00
---
## Dashboards

Two dashboards in the Signalwatch Grafana instance: **Fleet Overview** and **Host Drilldown**.

**Fleet Overview** is the landing page — time-series for CPU usage across all nodes, memory pressure, disk fill rate, and a red/green grid of alert states (one cell per host). Color-coded by severity. Useful for a quick "is anything on fire" check.

**Host Drilldown** breaks down to per-machine detail: CPU by core, disk I/O, network throughput in/out, and process listings sorted by RSS (memory is the first thing to blow up). I pin this dashboard during troubleshooting.

Both auto-refresh every 30 seconds. Provisioned via [[Grafana Provisioning as Code]] so they survive container restarts without manual recreation.
