---
id: 01JEV000000000000000000006
title: Atlas Incident 2025-02-14
type: incident
created: 2025-02-14T16:00:00Z
updated: 2025-02-18T10:00:00Z
tags: [atlas, incident, reliability]
---
# Atlas Incident 2025-02-14

## Summary

Cedar's clock drifted eleven minutes behind the API clock. Harbor rejected new batches because
their timestamps fell outside the accepted window. Collection continued locally, and all queued
readings were replayed after recovery; no sensor data was lost.

## Root cause

Verbose debug logs filled the gateway disk. The time-synchronization service could no longer write
its state and stopped correcting the clock. The ingestion errors were a symptom of the disk
exhaustion rather than a network fault.

## Recovery

The operator removed expired debug logs, restarted time synchronization, verified the clock, and
replayed Cedar's SQLite queue. Harbor accepted the backlog in chronological order.

## Follow-up actions

- Alert when gateway disk use exceeds 80 percent.
- Rotate debug logs after 100 MB.
- Quarantine and flag batches with up to fifteen minutes of skew instead of rejecting them outright.
- Add a clock-offset panel to the Beacon report.

