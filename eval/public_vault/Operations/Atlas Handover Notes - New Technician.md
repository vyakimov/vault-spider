---
id: 01JEV000000000000000000152
title: Atlas Handover Notes - New Technician
type: note
created: 2025-08-26T09:00:00Z
updated: 2026-02-05T12:00:00Z
tags: [atlas, operations]
---
# Atlas Handover Notes - New Technician

## Welcome to Atlas Operations

You have been assigned to support field operations across Atlas environmental-monitoring sites. This document covers essential concepts, common procedures, and escalation paths. Expect your first week to be shadowing, weeks 2-3 performing routine tasks under supervision, and full autonomy by week 4.

## Core Systems

Cedar is the field gateway deployed at each remote site. It collects data from environmental sensors, buffers readings locally, and submits batches to Harbor (the central ingestion API) every 15 minutes or when the local queue reaches 1,000 records. If wired connectivity fails, Cedar continues to buffer locally; upon reconnection, it submits accumulated batches in sequence.

Harbor receives batches, validates schema compliance, and streams accepted data into PostgreSQL. The dashboard visualizes operational metrics and sensor readings in near-real-time. PostgreSQL is the system of record and must never be accessed directly by field technicians; all data queries go through the dashboard.

## Monthly Maintenance Routine

On the last Tuesday of each month, perform these tasks at each assigned site:
- Clear Cedar's local log files (rotate logs, keep 4 weeks of history).
- Verify sensor hardware is free of corrosion, condensation, or physical damage.
- Document any hardware anomalies in the site log.
- Confirm wireless fallback modem (if deployed) connects and passes latency test.
- Generate a data export for the previous month and verify file integrity.

New technicians should refer to [[Atlas Meeting Notes - Q3 2025]] for Q3 2025 policy updates and recent operational decisions. If you encounter an issue not covered in the runbooks, escalate to the lead technician before attempting workarounds.

## Emergency Procedures

If Cedar loses connectivity for more than 2 hours and the local queue is full:
1. Perform a power cycle (off for 30 seconds, back on).
2. Verify Harbor ingestion API is reachable from your field device.
3. If still offline, escalate to on-call database administrator.

If you observe sensor readings that are wildly inconsistent (e.g., pressure readings jumping 50% in 10 seconds), flag the sensor for recalibration during the next site visit. Do not modify sensor configuration yourself.

## On-Call Support

You will be on-call every 4th week, rotating with two other technicians. The on-call phone number is provided in the team Slack channel. Response time target is 30 minutes for critical issues, 4 hours for standard requests. When on-call, carry your laptop and maintain mobile connectivity at all times.
