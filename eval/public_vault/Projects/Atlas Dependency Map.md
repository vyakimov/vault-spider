---
id: 01JEV000000000000000000198
title: Atlas Dependency Map
type: reference
created: 2024-01-11T09:00:00Z
updated: 2024-04-16T12:00:00Z
tags: [atlas, project]
---
# Atlas Dependency Map

## External Service Dependencies

Cedar depends on AWS IoT Core for secure device certificate management; revocation or certificate expiration blocks Harbor communication. PostgreSQL at AWS RDS is the persistent store for all processed readings and metadata; performance degradation propagates immediately to the dashboard query layer.

## Component Dependency Graph

- Cedar: depends on AWS IoT Core, requires network connectivity for HTTPS batch transmission
- Harbor (ingestion API): depends on PostgreSQL, validates all incoming batches against schema
- Dashboard: depends on PostgreSQL, cached queries via Redis for summary data
- Beacon (daily report generation): depends on PostgreSQL, reads 24-hour summaries

## Transitive Dependencies

The Beacon report service depends indirectly on Cedar through PostgreSQL; if Cedar stops transmitting, Beacon reports lack recent data but continue running. The dashboard's Redis cache creates an indirect dependency on cache invalidation logic; stale summaries can persist if invalidation fails.

## Risk Assessment

PostgreSQL represents a single point of failure. Cedar queue provides 72-hour buffering, mitigating short outages. AWS IoT Core outages prevent new transmissions but do not affect dashboard visibility of queued data already in PostgreSQL.
