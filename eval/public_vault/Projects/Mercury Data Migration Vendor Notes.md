---
id: 01JEV000000000000000000203
title: Mercury Data Migration Vendor Notes
type: note
created: 2025-06-16T09:00:00Z
updated: 2026-09-21T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Vendor Notes

## Vendor Selection

A specialized data platform vendor was contracted to advise on Parquet schema design and migration pipeline architecture. The vendor brings 8+ years of experience migrating petabyte-scale CSV repositories to columnar formats and has documented cost optimizations for analytical workloads.

## Technical Consultation Sessions

The vendor conducted architecture reviews focused on partition strategy (monthly time-based partitions recommended over date-range bucketing), compression codec selection (Snappy chosen for balance of speed and ratio), and query optimization for dashboards reading aggregated summaries.

## Implementation Support

The vendor provided reference implementation code in Apache Spark for the transformation pipeline, including schema validation and data quality checks. They demonstrated the pipeline on historical CSV samples before production deployment to identify edge cases in the existing schema.

## Licensing and Hosting Considerations

The vendor's software operates under open-source Apache License 2.0, enabling internal deployment on company infrastructure. Ongoing support is available through their consulting practice; a support contract was negotiated for three months post-launch to address deployment issues and performance tuning.
