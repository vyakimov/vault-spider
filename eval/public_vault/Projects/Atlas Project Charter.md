---
id: 01JEV000000000000000000189
title: Atlas Project Charter
type: reference
created: 2025-01-02T09:00:00Z
updated: 2025-04-07T12:00:00Z
tags: [atlas, project]
---
# Atlas Project Charter

## Project Vision

Establish a continent-wide environmental sensor network providing continuous, high-fidelity readings of atmospheric, soil, and water parameters at 500+ stations. Enable real-time climate monitoring and support policy research through open-access data.

## Scope

In scope:
- Design and deploy Cedar LoRaWAN gateways
- Build Harbor ingestion and validation API
- Operate PostgreSQL-based time-series store
- Develop web dashboard for data visualization and download

Out of scope:
- Sensor hardware design (source from vendors)
- Satellite uplink infrastructure
- Predictive modeling or AI analysis
- Third-party data fusion or integration

## Success Criteria

- 100 operating stations by end of 2024
- 99.5% data availability (uptime + completeness) per station
- < 5-minute end-to-end latency from sensor reading to dashboard refresh
- Zero critical incidents related to data loss or corruption

## Stakeholders

- **Sponsor:** Environmental Research Institute (Dr. Sarah Chen, VP)
- **Lead Architect:** Cedar platform design and Harbor API (Marcus Rodriguez)
- **Ops Lead:** Infrastructure and field deployment (Jamie Lee)
- **Data Steward:** Schema governance and retention policy (Dr. Anouk Verhoeven)

## Key Milestones

| Milestone | Target Date |
|-----------|-------------|
| Cedar prototype test | 2024-Q1 |
| Phase 1 deployment (5 stations) | 2024-Q2 |
| Phase 2 expansion (25 stations) | 2024-Q4 |
| Phase 3 scaling (100 stations) | 2025-Q2 |

## Constraints

- Total budget: $1.2M over 24 months
- Primary constraint: field deployment logistics in remote areas
- Dependency on vendor delivery schedules for hardware
