---
id: 01JEV000000000000000000132
title: Atlas On-call Rotation
type: schedule
created: 2025-06-06T09:00:00Z
updated: 2026-09-11T12:00:00Z
tags: [atlas, operations]
---
# Atlas On-call Rotation

## Weekly Schedule

The Atlas operational team maintains a weekly on-call rotation covering Monday 00:00 UTC through Sunday 23:59 UTC. Each engineer carries a phone-based escalation number and has SSH access to production systems.

| Week Starting | Primary On-Call | Secondary Backup | Handoff Date |
|---|---|---|---|
| 2026-07-28 | Alex Chen | Priya Desai | Sunday 22:00 UTC |
| 2026-08-04 | Priya Desai | Marcus Johnson | Sunday 22:00 UTC |
| 2026-08-11 | Marcus Johnson | Alex Chen | Sunday 22:00 UTC |
| 2026-08-18 | Alex Chen | Priya Desai | Sunday 22:00 UTC |

Rotation cycles every three weeks; secondary backup becomes primary in week 4.

## Alert Thresholds and Escalation

On-call engineers monitor dashboard alerts and Cedar gateway health. Initial alert response window: 15 minutes.

For critical incidents (storage capacity alerts, API rate limit exceedances), wake the secondary within 5 minutes. Both on-call engineers work together on [[Atlas Storage Capacity Planning]] assessments to determine if emergency provisioning is needed.

## Handoff Procedure

Outgoing on-call engineer briefs incoming engineer on any open incidents, recent maintenance activities, or known edge cases. The handoff call occurs at Sunday 22:00 UTC and is documented in a brief wiki note.

Contact the operations manager if unable to complete an assigned week due to vacation or illness. Swaps must be arranged at least 72 hours in advance and logged in this document.

## Related notes

- [[Atlas Storage Capacity Planning]]
