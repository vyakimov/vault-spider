---
updated: 2026-03-02T11:11:00
id: 01M6K000000000000000000009
created: 2026-02-02T10:07:00
---
# Signalwatch Uptime Checks

I added simple HTTP uptime checks for Larder and the Millwright reader alongside the existing Prometheus metrics stack. Useful for catching service crashes that metrics alone might miss.

## Implementation
Each check runs every 2 minutes from the Signalwatch agent and hits a `/health` endpoint. If a service misses 3 consecutive checks, a warning alert fires. For Larder, I check both the web UI and the API backend separately since they're split processes.

## Tuning
Originally I had the interval at 30 seconds, which generated too much noise in the logs. Two minutes is a good balance—I catch downtime within a few minutes but don't waste bandwidth. Failures are also double-checked against the DNS resolver to rule out transient network hiccups.
