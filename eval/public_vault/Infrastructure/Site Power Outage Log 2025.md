---
id: 01JEV000000000000000000096
title: Site Power Outage Log 2025
aliases: []
type: log
created: 2024-06-15T09:00:00Z
updated: 2025-09-20T12:00:00Z
tags: [infrastructure, power]
---
# Site Power Outage Log 2025

## Year-to-Date Outage Record

The 2025 power outage frequency shows improvement over historical baselines, with only three utility-related incidents recorded through September. No generation system failures have occurred; all automatic failover events activated within specification.

| Date | Time (UTC) | Duration | Site | Cause | Impact | Notes |
|------|-----------|----------|------|-------|--------|-------|
| 2025-02-03 | 11:14 | 1 min 28 s | Primary office | Utility transient (wind damage, temporary branch contact) | None (UPS sustained load) | Utility restored without manual intervention |
| 2025-04-17 | 22:40 | 42 seconds | Ridge site only | Localized utility outage (pole-mounted transformer) | None (solar PoE reserve active) | Unplanned; no advance notice from utility |
| 2025-08-11 | 07:22 | 2 min 19 s | Primary office + Tower | Regional brown-out event (voltage sag to 94 V AC) | None (exceeded UPS dropout threshold by 2 seconds; battery engaged) | Utility notification delayed; post-event analysis shows power remained above critical load threshold |

## Outage Severity Assessment

All three 2025 incidents resulted in **zero telemetry loss** and **zero equipment damage**. The facility's distributed backup power infrastructure (combination UPS, solar battery bank, and standby generator) successfully maintained mission continuity in all cases.

- **Total cumulative outage time:** 4 minutes 29 seconds (vs. 31 min 40 s in 2024)
- **Improvement factor:** 7.1× reduction from 2024
- **Average incident duration:** 1 min 29 s
- **Generator activation events:** 0 (no outages exceeded UPS + solar reserve capacity)

## Forecast and Preventive Planning

The regional utility has announced two planned maintenance windows in Q4 2025 (October 12 and November 8). Both events will be coordinated with facility scheduling to allow pre-positioning of backup systems and load deferral if needed.

Weather forecasts indicate potential for elevated lightning activity in late autumn; grounding system inspection is scheduled for late September to ensure optimal surge protection status.

---
**Year-end review:** pending completion in December 2025
