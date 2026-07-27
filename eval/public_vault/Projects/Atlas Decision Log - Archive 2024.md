---
id: 01JEV000000000000000000186
title: Atlas Decision Log - Archive 2024
type: decision-log
created: 2024-07-25T09:00:00Z
updated: 2024-01-04T12:00:00Z
tags: [atlas, project]
---
# Atlas Decision Log - Archive 2024

## Decision: LoRaWAN Over Cellular Direct

**Date:** 2024-01-12 | **Status:** Approved

Gateway architecture would use LoRaWAN for sensor-to-gateway communication rather than direct cellular sensors. Rationale: LoRaWAN's range and power efficiency better suited field deployment; cellular module cost and battery consumption per sensor prohibited distributed placement. This decision cascaded into Cedar gateway requirements and defined the Harbor ingestion API shape.

## Decision: PostgreSQL for Time-Series Storage

**Date:** 2024-02-08 | **Status:** Approved

After evaluating TimescaleDB, ClickHouse, and InfluxDB, selected PostgreSQL with time-series optimization. PostgreSQL's table partitioning support, JSONB flexibility for metadata, and team expertise reduced operational risk. Dashboard and reporting would query via stored procedures.

## Decision: Three-Tier Field Deployment Cadence

**Date:** 2024-03-15 | **Status:** Approved

Deploy in phases: Phase 1 (five reference stations for data collection), Phase 2 (regional expansion), Phase 3 (continent-wide coverage). This staged approach allowed validation of Cedar behavior and sensor calibration before full-scale rollout.

## Related Decisions and Plans

See [[Atlas Milestone Tracker]] for completion tracking of Phase 1–2 deployments. [[Atlas Sensor Hub Retrospective 2024]] documents what we learned from the initial rollout. The [[Atlas Project Charter]] established the original scope that these decisions were made within.

Key technical decisions are maintained in [[Atlas Sensor Hub Lessons Learned]] (2024 operational insights) and [[Atlas Sensor Hub Data Model]] (schema decisions). See also [[Atlas Sensor Hub Architecture]] for the resulting system design.

## Notes

Archive closed 2024-12-31. Decisions from 2025 onward are in the running decision log.
