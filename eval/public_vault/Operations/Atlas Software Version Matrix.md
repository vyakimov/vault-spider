---
id: 01JEV000000000000000000155
title: Atlas Software Version Matrix
type: reference
created: 2024-02-03T09:00:00Z
updated: 2025-05-08T12:00:00Z
tags: [atlas, operations]
---
# Atlas Software Version Matrix

## Current Deployment Versions

| Component | Location | Version | Release Date | Deployed Date |
|-----------|----------|---------|--------------|---|
| Cedar Gateway | North Ridge | 4.2.1 | 2025-02-14 | 2025-02-20 |
| Cedar Gateway | East Valley | 4.2.1 | 2025-02-14 | 2025-02-20 |
| Cedar Gateway | South Marsh | 4.1.8 | 2025-01-09 | 2025-01-11 |
| Cedar Gateway | West Peak | 4.2.0 | 2025-02-01 | 2025-02-15 |
| Harbor API | Central | 2.8.7 | 2025-01-30 | 2025-02-03 |
| PostgreSQL | Central | 14.7 | 2024-11-08 | 2024-11-15 |
| Dashboard | Central | 3.1.4 | 2025-02-10 | 2025-02-12 |

## Version Support and Lifecycle

Cedar firmware versions 4.1.x and 4.2.x are in active support. Version 4.0.x reached end-of-life on 2024-12-31 and is no longer receiving security patches. Harbor API 2.8.x is current; version 2.7.x remains supported until 2025-08-31. PostgreSQL 14.7 is the target version for all deployments; migration from PostgreSQL 13 is in progress at two legacy sites.

## Compatibility Matrix

Harbor API 2.8.7 is compatible with Cedar firmware 4.1.5 through 4.2.1. Dashboard 3.1.4 requires PostgreSQL 13.8 or later; versions 3.0.x are compatible with PostgreSQL 12. Harbor API does not support Cedar firmware versions below 4.0.6 (legacy firmware reached EOL in early 2024).

## Pending Version Updates

South Marsh Cedar gateway (currently 4.1.8) is scheduled for upgrade to 4.2.1 during the next maintenance window (planned for March 2025). PostgreSQL upgrade from 13.9 to 14.7 at West Peak is planned for Q2 2025 during a scheduled maintenance window. No pending updates are required for Harbor API or Dashboard at this time.

## Version Anomalies and Exceptions

None currently documented. All deployed versions are stable and compatible with the existing infrastructure. Deviations from this matrix must be approved by the operations lead and documented in an architecture decision record.
