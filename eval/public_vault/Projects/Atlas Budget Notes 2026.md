---
id: 01JEV000000000000000000192
title: Atlas Budget Notes 2026
type: note
created: 2024-04-05T09:00:00Z
updated: 2024-07-10T12:00:00Z
tags: [atlas, project]
---
# Atlas Budget Notes 2026

## Capital Expenditure

Cedar gateway hardware (Phase 3 scaling): 80 units @ $1,100 per unit = $88,000
Sensor modules (environmental, soil, water suites): $156,000
Network edge infrastructure (backup power, radio repeaters): $32,000
Data center upgrades (PostgreSQL storage expansion, backup systems): $45,000

**CapEx Subtotal:** $321,000

## Operational Expenses

Personnel (4 FTE engineers + technicians): $380,000
Cloud hosting and cellular contracts: $95,000
Travel and field logistics: $42,000
Maintenance and spare parts: $28,000
Professional services (compliance audit, security review): $15,000

**OpEx Subtotal:** $560,000

## Data Infrastructure Budget

Storage and archival: $18,000 (PostgreSQL SSD expansion, cold-storage backup)
Monitoring and alerting software licenses: $8,000
Dashboard and visualization tools: $5,000

**Data Total:** $31,000

## Budget Constraints and Decisions

Data retention policy (documented in [[Atlas Sensor Hub Data Model]]) sets 90-day retention for raw readings, indefinite for summaries. This decision reduces storage costs by 35% versus keeping all raw data indefinitely, but required schema redesign to summarize efficiently.

**Total 2026 Budget Request:** $912,000

**Status:** Under review by finance committee; contingent on Phase 2 deployment success.
