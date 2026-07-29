---
id: 01JEV000000000000000000147
title: Atlas Backup Policy Draft 2023
type: note
created: 2024-03-21T09:00:00Z
updated: 2025-06-26T12:00:00Z
tags: [atlas, operations]
---
# Atlas Backup Policy Draft 2023

## Original Proposal

This draft was circulated in March 2024 as part of disaster-recovery planning. The original proposal advocated for continuous point-in-time recovery capability, requiring PostgreSQL WAL archival to S3 every 5 minutes and full backups every Sunday. Recovery time objective was set at 2 hours with a recovery point objective of 15 minutes. The draft was reviewed by five operators and two external consultants.

## Feedback and Reasons for Revision

Operational feedback indicated that continuous S3 archival added significant latency to Cedar's batch ingestion pipeline during peak hours. Cost analysis showed that the proposed 15-minute RPO would require backup storage to grow by 8.2TB annually versus 3.1TB under less frequent snapshots. The 2-hour RTO was challenged as impractical given network latency at field sites and the time required for migration validation. A revised policy was adopted in late 2024 with different retention and frequency targets better suited to operational reality.

## Technical Decisions Deferred

The draft proposed automated restoration testing as part of the backup verification pipeline, but implementation was deferred pending completion of the staging environment build-out. Archive compression algorithms were left unspecified pending performance benchmarking. The decision to use local encrypted storage on the backup appliance versus remote archival was left open for further cost modeling.
