---
id: 01JEV000000000000000000140
title: Atlas Database Maintenance Window Procedure
type: procedure
created: 2025-05-14T09:00:00Z
updated: 2026-08-19T12:00:00Z
tags: [atlas, operations]
---
# Atlas Database Maintenance Window Procedure

## Overview

This procedure describes how to perform brief PostgreSQL maintenance (index rebuilds, VACUUM, schema updates) without interrupting Cedar's ability to queue incoming sensor batches. The key is that Harbor API and Cedar gateway continue operating in a queued mode while the dashboard becomes temporarily unavailable.

## Pre-Maintenance Checklist

1. Schedule the maintenance window during lowest expected traffic (typically 02:00–04:00 UTC)
2. Notify on-call team and any dependent services at least 48 hours in advance
3. Ensure a rollback plan exists (previous database backup, recovery scripts)
4. Verify Cedar gateway has sufficient local queue capacity for expected batch volume during maintenance
5. Stop any automated ETL jobs that read from PostgreSQL

## Maintenance Steps

1. **Pause Dashboard Application**
   - The dashboard application gracefully shuts down; Harbor API remains active
   - Existing user sessions receive a "maintenance window" message

2. **Establish Cedar Queue Isolation**
   - Harbor API continues accepting batches and writing to disk/queue (not to PostgreSQL)
   - Verify Cedar backlog is being populated by checking queue directory on Harbor server
   - Typical queue grows at 5–10 batches per minute under normal load

3. **Perform PostgreSQL Maintenance** (target: <30 minutes)
   - Common tasks: `REINDEX`, `VACUUM ANALYZE`, schema backfills, index drops
   - Ensure no long-running transactions block the maintenance
   - Monitor PostgreSQL log for errors

4. **Resume Database Operations**
   - Start dashboard application
   - Verify dashboard can connect to PostgreSQL and respond to test queries
   - Check that queued batches have been successfully flushed to the database

## Post-Maintenance Verification

1. Confirm dashboard displays current sensor readings (within 1-minute freshness)
2. Spot-check Cedar gateway status in the dashboard UI
3. Log the maintenance event (timestamp, duration, work performed) in the operations wiki
4. Alert on-call team that maintenance is complete and monitoring has resumed normal thresholds

Expected total downtime: 30–45 minutes including pre and post checks.
