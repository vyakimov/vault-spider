---
id: 01JEV000000000000000000134
title: Atlas Incident Severity Levels
type: reference
created: 2025-08-08T09:00:00Z
updated: 2026-02-13T12:00:00Z
tags: [atlas, operations]
---
# Atlas Incident Severity Levels

## Definition Framework

Incidents are classified at time of report to determine escalation and response SLAs. Classification may be updated as more information becomes available.

## Severity 1: Critical

**Criteria:**
- Dashboard completely unavailable or unresponsive to all users (>5 min)
- Cedar gateway unable to receive or queue sensor batches
- PostgreSQL database offline or data corruption detected
- Entire production system unreachable (network/infrastructure failure)

**Response SLA:** 15 minutes to acknowledge; incident commander assigned within 5 minutes.

**Example incidents:**
- Harbor API crashed; Cedar batches are rejected and lost
- PostgreSQL storage filled to 100%; no new sensor readings can be written
- Network partition between Cedar and Harbor (Cedar queue fills to capacity)

## Severity 2: High

**Criteria:**
- Single Cedar gateway station offline (others operational)
- Dashboard degradation: response times >10 seconds or specific feature broken
- Data quality issue affecting <5% of readings (caught by validation rules)
- Scheduled maintenance window exceeded by >50%

**Response SLA:** 30 minutes acknowledgment; email escalation to manager.

**Example incidents:**
- One cellular modem connection drops; site buffers locally but cannot transmit
- Dashboard query timeout causes some charts to fail loading
- Sensor calibration drift detected on one unit

## Severity 3: Low

**Criteria:**
- Non-critical feature degradation (e.g., export functionality slow)
- Documentation outdated
- Scheduled maintenance window exceeded by <50%
- Cosmetic UI bugs with no data loss

**Response SLA:** Next business day; ticket assignment and triage.

All incidents are logged with timestamp, assignee, and resolution time. Severity 1 incidents trigger post-incident review; Severity 2 incidents are tracked for recurring pattern detection (see [[Atlas Software Version Matrix]]).
