---
id: 01JEV000000000000000000159
title: Atlas Meeting Notes - Q1 2025
type: note
created: 2024-06-07T09:00:00Z
updated: 2025-09-12T12:00:00Z
tags: [atlas, operations]
---
# Atlas Meeting Notes - Q1 2025

## Attendance and Date

Quarterly operations meeting held January 22, 2025. Attendees: Operations Lead, 4 field technicians, Database Administrator, Harbor API developer, Dashboard developer, and Site Reliability Engineer.

## Incident Follow-ups

The Harbor API connection pool exhaustion incident from December was reviewed. Root cause was identified as a resource leak in connection handling following timeouts. A patch was deployed January 8th, and no recurrence has been observed. The team discussed implementing more robust connection monitoring.

## Staffing Changes

Two field technicians will transition to other projects by end of Q1. The team approved hiring two new technicians (onboarding target: mid-February). Initial training will focus on site assessment procedures and basic troubleshooting. Existing technicians will each mentor one new team member for the first month.

## Upcoming Projects and Decisions

**Cellular Modems**: [[Atlas Vendor Evaluation - Cellular Modems]] evaluation is underway. Three candidates are being tested at pilot sites. Budget approval is expected by end of Q1; deployment would follow in Q2.

**Deployment Process**: Review of [[Atlas Deployment Checklist]] identified several missing pre-flight checks. Revisions are being finalized and will be rolled out for the next Harbor API release (target: mid-February).

**Database Maintenance Windows**: [[Atlas Database Maintenance Window Procedure]] is being revised to reduce downtime and improve communication with Harbor clients. New procedure prioritizes minimal disruption and provides 24-hour advance notifications.

## Maintenance and Alert Tuning

**Alert Thresholds**: [[Atlas Monitoring Alert Rules]] require review and tuning. Several false alarms were triggered in December due to overly aggressive CPU and disk usage thresholds. The SRE will propose revised thresholds for feedback.

**Sensor Calibration**: [[Atlas Sensor Calibration Log 2025]] was reviewed. Four sensors showed calibration drift in pressure readings. Recalibration is scheduled for February at the affected sites. The team will establish a formal recalibration schedule (proposed: semi-annual).

## Infrastructure and Network

The team reviewed [[Service Port Registry]] to ensure all services are using assigned ports correctly. One service (internal monitoring agent) was found using an unregistered port; it has been assigned port 8764 and the registry updated.

## Next Steps

- Hiring process to be accelerated (new technicians needed by late February).
- Cellular modem vendor decision by February 28th.
- Deployment checklist and database maintenance procedure rollouts by mid-February.
- Alert threshold tuning and deployment by mid-February.
- Next quarterly meeting: April 22, 2025.
