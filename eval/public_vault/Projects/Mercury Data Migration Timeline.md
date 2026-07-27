---
id: 01JEV000000000000000000210
title: Mercury Data Migration Timeline
type: reference
created: 2024-04-23T09:00:00Z
updated: 2024-07-02T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Timeline

## Phase 1: Planning and Design (January - March 2024)

Vendor selection and architecture review conducted in January. Schema mapping prototype completed by mid-February. See [[Atlas Budget Notes 2026]] for allocated resources and [[Atlas Project Glossary]] for terminology. Pilot transformation of 100M records completed by end of March, validating pipeline performance.

## Phase 2: Historical Data Migration (April - June 2024)

Transformation of 8.5-year archive (2.3B records) distributed across 12 parallel workers. Partition strategy implemented with monthly boundaries. Weekly validation checkpoints verified row count preservation and field-level data integrity. See [[Mercury Observation Equipment List]] for equipment allocation during testing phases.

## Phase 3: Live Ingestion Cutover (July 2024)

All new data routed to Parquet-backed storage on July 15. Dashboard queries updated to read from new schema. Legacy CSV ingestion halted after 48-hour parallel operation window. See [[Atlas Sensor Hub Load Test Results]] for performance benchmarks and [[Atlas Sensor Vendor Evaluation - Enclosures]] for infrastructure changes.

## Phase 4: Archive and Cleanup (August 2024)

CSV export archives compressed and stored on archival media. See [[Atlas Sensor Hub Decommission Plan - Old Loggers]] for data retention policies. Parquet validation continued through August 31; project marked complete by September 1, 2024.
