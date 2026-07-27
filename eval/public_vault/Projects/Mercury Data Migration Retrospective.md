---
id: 01JEV000000000000000000204
title: Mercury Data Migration Retrospective
type: review
created: 2024-07-17T09:00:00Z
updated: 2024-01-22T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Retrospective

## Project Completion Summary

The CSV-to-Parquet migration successfully converted 8.5 years of historical data (2.3B records) into columnar format and transitioned all live ingestion to Parquet-backed storage. The project ran from planning phase (January 2024) through production validation (July 2024), completing ahead of schedule.

## What Went Well

The phased approach of migrating historical data first, then switching live ingestion in a separate cutover, reduced risk significantly. Vendor consultation during architecture phase identified partition strategy early, preventing costly redesigns mid-project. Comprehensive test plan caught schema ambiguities before production deployment.

## Challenges and Resolutions

Initial performance benchmarks showed transformation throughput was 20% below target on the reference hardware; parallelizing the Spark pipeline across 12 workers instead of 4 resolved the bottleneck. See [[Mercury Data Migration Schema Diff]] for details on field mapping complexities that required manual resolution.

## Lessons for Future Migrations

Invest in data quality assessment before cutover. Plan for at least two weeks of validation testing even if development completes early. Document partition key selection rationale to enable future schema evolutions. Maintain CSV export capability as a long-term archive strategy, not just a rollback escape hatch.
