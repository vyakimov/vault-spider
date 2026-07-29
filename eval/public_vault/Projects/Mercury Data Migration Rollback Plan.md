---
id: 01JEV000000000000000000202
title: Mercury Data Migration Rollback Plan
type: plan
created: 2024-05-15T09:00:00Z
updated: 2025-08-20T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Rollback Plan

## Trigger Conditions

Rollback is initiated if validation detects: schema mismatches in >0.1% of migrated records, data loss identified by row count discrepancies, or transformation errors affecting critical fields like timestamps or sensor identifiers. The on-call engineer must notify leadership within 1 hour of discovering a trigger condition.

## Rollback Execution Steps

1. Stop all Parquet ingestion jobs and revert storage layer routing to legacy CSV pipeline
2. Restore PostgreSQL views to read from CSV export tables instead of Parquet-backed views
3. Verify that downstream consumers (dashboard, reports, analytics) successfully fall back to CSV sources
4. Preserve Parquet-formatted data on archival storage for forensic analysis

## Recovery Timeline

Cold failover to CSV pipeline takes approximately 15 minutes: 5 minutes to stop Parquet jobs, 5 minutes to update database views, 5 minutes to smoke-test dashboard queries. Warm failover (maintaining dual pipelines temporarily) extends timeline to 30 minutes but reduces risk of query failures during transition.

## Post-Rollback Investigation

Analyze transformation logs and compare Parquet output with source CSV to identify systematic errors. Engage storage vendor for technical support; reference [[Mercury Data Migration]] project documentation and [[Mercury Transit Prediction Notes]] for context. Coordinate with teams listed in [[Atlas Sensor Hub Contractor Agreement]] and [[Atlas Milestone Tracker]]. See also [[Atlas Sensor Hub Decommission Plan - Old Loggers]] for archival of old logger data and [[Atlas Incident 2025-05-19]] for a similar incident precedent.
