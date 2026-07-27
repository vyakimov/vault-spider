---
id: 01JEV000000000000000000135
title: Atlas Data Quality Checks
type: reference
created: 2024-09-09T09:00:00Z
updated: 2025-03-14T12:00:00Z
tags: [atlas, operations]
---
# Atlas Data Quality Checks

## Automated Validation Pipeline

Harbor ingestion API runs a suite of validation rules on each incoming sensor batch before writing to PostgreSQL. Flagged readings are logged separately and do not appear in the main dataset or on the dashboard.

## Primary Checks

**Temperature Range Validation**
- Reject if outside −15°C to +60°C (beyond physical Cedar enclosure operating range)
- Flag if reading changes >5°C from previous sample (possible sensor noise or failure)
- Alert threshold: >2% of batch readings flagged

**Humidity Bounds**
- Reject if outside 5–98% (sensor saturation at extremes)
- Flag if differential >15% from previous 10-minute window
- Applied across all [[Atlas Sensor Calibration Log 2024]] and calibrated units

**Batch Metadata Validation**
- Require Cedar device ID, timestamp, and batch sequence number
- Reject if timestamp is future-dated or >72 hours in the past
- Reject if sequence number is out of order (potential data loss indicator)

**Rate-of-Change Analysis**
- Monitor typical sensor behavior patterns; flag anomalies
- Example: humidity change >30% in 5 minutes warrants investigation
- Used by the dashboard to suggest when manual inspection is needed

## Escalation to Operations

When >5% of batches are flagged within a 1-hour window, an alert is sent to the on-call engineer via [[Atlas API Rate Limits]] monitoring. The alert includes the specific failing field gateway and rule(s) violated.

Common causes (from [[Atlas Access Review 2024]] remediation and [[Atlas Storage Capacity Planning]] reviews):
- Sensor calibration drift (address via [[Atlas Telemetry Runbook]])
- Network packet loss causing timestamp skew
- Cedar local queue corruption after power event

## Historical Data Reporting

Flagged readings are retained separately for audit purposes and can be queried by operations staff using restricted PostgreSQL views. This maintains data integrity on the main dashboard while preserving investigative capability.

Related quality topics are documented in [[Atlas Deployment Checklist]] (sensor installation verification) and vendor procedures in [[Atlas Third-Party Audit 2025]].

## Related notes

- [[Atlas API Rate Limits]]
- [[Atlas Access Review 2024]]
- [[Atlas Storage Capacity Planning]]
- [[Atlas Sensor Calibration Log 2024]]
- [[Atlas Deployment Checklist]]
- [[Atlas Telemetry Runbook]]
