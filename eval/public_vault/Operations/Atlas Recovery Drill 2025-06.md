---
id: 01JEV000000000000000000148
title: Atlas Recovery Drill 2025-06
type: exercise
created: 2025-04-22T09:00:00Z
updated: 2025-07-01T12:00:00Z
tags: [atlas, operations]
---
# Atlas Recovery Drill 2025-06

## Scenario and Timeline

The June 2025 recovery drill tested a PostgreSQL storage failure scenario where the primary database volume became unreachable while the backup appliance remained online. The drill began at 14:00 UTC on June 28th. Operators initiated recovery from the previous night's incremental backup, requiring 12 minutes to restore schema and indices, followed by 8 minutes to stream transaction logs and verify consistency. Dashboard reconnection required an additional 6 minutes to clear cached connection states.

Total recovery time was 26 minutes against a 3-hour objective. The drill revealed that Harbor API clients timed out after 90 seconds of unavailability, requiring a post-recovery client reconciliation window. Cedar field gateways maintained their local ingestion queues throughout the outage without data loss.

## Findings and Action Items

The primary finding was that database connection pooling in the dashboard still held references to old connection strings after failover, causing 180-second recovery delays. A code fix was implemented to flush connection state more aggressively, reducing the failover window from 6 minutes to 2 minutes. The Harbor API timeout behavior was documented as working as designed; clients at three sites were updated to increase their timeout thresholds from 90 to 120 seconds.

A secondary finding came from [[Atlas Site Visit Log 2024]] review: that field site local storage for Cedar is often full during extended outages, limiting queue depth. Site operations were instructed to perform disk cleanup as part of the monthly maintenance window.

## Participants and Sign-off

The drill involved four on-call operators, the database administrator, and two Harbor API developers. All teams confirmed readiness to execute the recovery procedure in production. The exercise is scheduled to be repeated in Q4 2025 under a different failure scenario.
