---
id: 01JEV000000000000000000146
title: Atlas Password Rotation Schedule
type: schedule
created: 2025-02-20T09:00:00Z
updated: 2026-05-25T12:00:00Z
tags: [atlas, operations]
---
# Atlas Password Rotation Schedule

## API Service Accounts

Harbor ingestion API credentials rotate every 90 days. Cedar field gateway administrative passwords are changed on a 120-day cycle, coordinated with quarterly site visits to avoid synchronization issues. The dashboard read-only query account password rotates every 180 days since it requires coordination across multiple dashboard instances. All rotations are scheduled for Tuesday nights between 22:00 and 02:00 UTC to minimize dashboard query latency during peak hours in US timezones.

## Database Administrative Accounts

PostgreSQL superuser and replication accounts rotate on a 180-day schedule. The nightly backup account (used only for exports and verification queries) rotates every 270 days since password changes require coordination with scheduled backup windows. Emergency break-glass accounts are rotated immediately following any incident requiring their use, and at minimum annually.

## Notification and Tracking

Rotation deadlines are tracked in the centralized operations calendar with 14-day advance notifications sent to on-call operators. Failed rotations are escalated within 24 hours to the lead database administrator. No credentials are stored or logged in these notes; actual password values and rotation execution records are maintained in the secure credential vault.
