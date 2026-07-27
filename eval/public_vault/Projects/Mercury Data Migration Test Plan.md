---
id: 01JEV000000000000000000201
title: Mercury Data Migration Test Plan
type: plan
created: 2025-04-14T09:00:00Z
updated: 2025-07-19T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Test Plan

## Functional Test Cases

- **Schema Validation**: Verify that each migrated record contains all required fields and data types match the Parquet schema specification
- **Boundary Conditions**: Test migration of records at schema transition dates (2023-01-01 cutover) and edge values (minimum/maximum field ranges)
- **Data Completeness**: Confirm that record counts and checksums match between source CSV files and output Parquet partitions

## Performance Test Cases

Load test the migration pipeline with compressed archive containing 500M rows across 10 parallel workers. Measure throughput (rows/second), peak memory usage, and disk I/O patterns. Verify that transformation runtime scales linearly with input size up to 1B rows.

## Regression Test Cases

Run the migration pipeline on historical CSV exports and compare output against previously validated reference Parquet files. This ensures that schema fixes in recent migration versions do not alter previously-converted data.

## Manual Validation Steps

Sample 1000 records randomly from each month-long partition and manually inspect field-by-field against corresponding source CSV rows. Document any anomalies or malformed output for investigation before cutover approval.
