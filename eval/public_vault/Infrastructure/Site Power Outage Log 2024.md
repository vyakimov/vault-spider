---
id: 01JEV000000000000000000095
title: Site Power Outage Log 2024
aliases: []
type: log
created: 2025-05-14T09:00:00Z
updated: 2026-08-19T12:00:00Z
tags: [infrastructure, power]
---
# Site Power Outage Log 2024

## Recorded Power Interruptions

This log documents all instances in 2024 where primary utility AC power was lost for 30 seconds or more at any field site. Outages are correlated with regional power utility incident reports and weather event logs to identify root causes.

| Date | Time (UTC) | Duration | Site | Cause | Generator Activation | Notes |
|------|-----------|----------|------|-------|---------------------|-------|
| 2024-01-14 | 14:22 | 2 min 45 s | Primary office | Utility fault (pole damage) | Yes (startup 3 sec) | Regional ice storm; no data loss |
| 2024-03-08 | 08:07 | 47 seconds | Tower site | Unknown (sensor not recording) | N/A (solar system kept PoE running) | Incident report filed with utility |
| 2024-05-19 | 19:31 | 18 min 12 s | Primary office | Transformer fire (neighboring site) | Yes (immediate) | Longest outage of year; UPS sustained critical loads |
| 2024-07-02 | 12:08 | 1 min 33 s | All sites (regional) | Utility maintenance (planned, unannounced) | Partial (office generator failed to start—see 2024-07-03 note) | Investigation triggered; generator test performed July 3 |
| 2024-09-14 | 03:44 | 3 min 22 s | Tower site | Weather-induced transient (lightning near pole) | N/A (automatic transfer to 10 kWh solar reserve) | Complete mission success; no telemetry gap |
| 2024-11-22 | 16:55 | 5 min 8 s | Primary office | Equipment maintenance (utility scheduled) | Yes (pre-notification allowed full load takeover) | Maintenance window logged in advance; generator test concurrent |

## Summary Statistics

- **Total outage time in 2024:** 31 minutes 40 seconds across all sites
- **Average outage duration:** 5 min 16 s (median: 2 min 55 s)
- **Most common cause:** Utility infrastructure events (70% of incidents)
- **Generator activation success rate:** 5/5 (100% availability when called)
- **Data continuity:** 100% (no telemetry loss during any outage)

The 2024 performance is significantly better than the 2023 baseline (7 outages, 89 minutes total), reflecting improvement in local grid stability and completion of utility hardening projects in the region.

## Related Operations

All outage events are cross-referenced with the [[Battery Bank Maintenance Log|battery bank status logs]] to verify that backup power systems operated within specification. Generator load test results (see [[Generator Maintenance Log]]) confirm hardware readiness for future events.

Regional outage forecasts are monitored during severe weather seasons (winter/spring and fall) to enable proactive load shedding if needed.

---
**Next review:** 2024-12-31 (annual summary report due)
