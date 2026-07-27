---
id: 01JEV000000000000000000143
title: Atlas Log Retention Policy
type: policy
created: 2024-08-17T09:00:00Z
updated: 2025-02-22T12:00:00Z
tags: [atlas, operations]
---
# Atlas Log Retention Policy

## Scope

This policy applies to **application and access logs** (Cedar gateway logs, Harbor API logs, dashboard application logs, PostgreSQL query logs). This is distinct from the retention of **sensor reading data**, which is governed separately by long-term data archival policies.

## Retention Periods

**Cedar Gateway Logs**
- Retain on-device: 7 days (local storage constraint)
- Archive to central logging system: 90 days
- Purge after: 1 year
- Reason: Diagnostics for connectivity issues, firmware behavior, queue flushing events

**Harbor API Logs**
- Application logs: 30 days (live system), 1 year archived
- Request/response logs (sanitized): 30 days (live), 90 days archived
- Error logs (full retention): 2 years (may contain sensitive circuit details)
- Reason: Regulatory compliance for API audit trails; batch ingestion troubleshooting

**Dashboard Application Logs**
- Access logs (IP, timestamp, endpoint): 30 days
- Error logs: 90 days
- User action logs: 1 year (who queried what, when)
- Reason: Performance debugging, security incident investigation

**PostgreSQL Query Logs**
- Slow-query log (>500ms queries): 30 days
- General query log (when enabled during troubleshooting): 7 days (high I/O overhead)
- Transaction logs (WAL): Kept until backed up; see [[Atlas Backup Policy Draft 2023]] for backup frequency
- Reason: Performance tuning, audit trail for data access

## Access Control

Logs are segregated by role per [[Atlas Access Review 2024]]:
- **Cedar technicians:** Can access their own device logs for 30 days
- **Operations engineers:** Full access to all logs within their retention window
- **Security auditors:** Can request archived logs for compliance reviews

Archive storage is managed by [[Atlas Deployment Checklist]] validation and [[Atlas Vendor Evaluation - Cellular Modems]] vendor compliance coordination.

## Automated Rotation

Log rotation is handled by logrotate (see `/etc/logrotate.d/atlas-*` configuration) running daily. Compressed archives are moved to the central logging backend (e.g., syslog aggregator or cloud logging service) for long-term retention.

Manual log purges can be triggered by the on-call engineer if disk space becomes critical (see [[Atlas Sensor Calibration Log 2025]] on-call procedures for emergency escalation).

Audit of log retention compliance occurs quarterly; results are documented in [[Atlas Telemetry Runbook]] incident reviews.

## Related notes

- [[Atlas Deployment Checklist]]
- [[Atlas Vendor Evaluation - Cellular Modems]]
- [[Atlas Sensor Calibration Log 2025]]
- [[Atlas Access Review 2024]]
- [[Atlas Backup Policy Draft 2023]]
- [[Atlas Telemetry Runbook]]
