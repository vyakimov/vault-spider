---
id: 01JEV000000000000000000185
title: Atlas Incident 2025-08-02
type: incident
created: 2025-06-24T09:00:00Z
updated: 2026-09-03T12:00:00Z
tags: [atlas, project]
---
# Atlas Incident 2025-08-02

## Incident Summary

A misconfigured alert rule in the Harbor alerting engine generated false positives for every Cedar station, paging the on-call technician 187 times over 3.5 hours on August 2, 2025. Alert rule `high_batch_latency_consecutive` was deployed with a 5-minute aggregation window but no cooldown, causing each Cedar to trigger the alert independently every sampling cycle rather than once per anomaly.

## Timeline

- 08:15 UTC: Alert rule deployed as part of expanded monitoring for data-freshness compliance
- 08:17 UTC: First batch of alerts delivered; PagerDuty spam detection disabled after 10 messages
- 08:18 UTC: On-call technician acknowledged incident; Cedar metrics show normal batch rates and latencies
- 08:22 UTC: Root cause suspected; operations team began manual rule disablement
- 08:52 UTC: Alert rule silenced; remaining queued notifications cleared from queue
- 09:35 UTC: Alert rule rewritten with 1-hour cooldown and whitelist for known transient latency spikes

## Impact

Alert fatigue and system distraction. No Atlas data loss or missed readings. Carrier network and Cedar behavior remained normal throughout. Investigation time: 37 minutes from first alert to silencing.

## Preventive Measures

Updated alert deployment checklist (referenced in [[Atlas Sensor Hub Contractor Agreement]]) to require:
- Canary deployment to single test gateway for 24 hours
- Review of alert firing frequency against historical data
- Mandatory cooldown/de-duplication on multi-station rules
- Slack webhook notification for alert rule changes (audit trail)

## Lessons

Alert rules must be tested against baseline metrics before production deployment. Implement alert rule dry-run testing in CI/CD.
