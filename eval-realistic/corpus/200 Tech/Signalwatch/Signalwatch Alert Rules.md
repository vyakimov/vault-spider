---
tags:
  - homelab
updated: 2026-06-05T10:11:00
id: 01M6K000000000000000000002
created: 2026-02-02T09:07:00
---
## Alert Rules

The production rules are split between host-level and network-level. Disk space fires at 85% used; CPU context switches at 50k/sec; memory at 80%. Tailnet link-down alerts if any node vanishes for more than 2 minutes (filtered to skip maintenance windows via labels).

**Distinct from Atlas thresholds:** Atlas has stricter alerting for production services, but the homelab rules are tuned for hardware aging and expected low-grade flapping. I've burned out disks by ignoring early warnings, so I err on the side of noise rather than silent failures.

Slack integration pushes critical+warning to a dedicated channel. False-positive cleanup is tracked in [[Signalwatch False Positives]].
