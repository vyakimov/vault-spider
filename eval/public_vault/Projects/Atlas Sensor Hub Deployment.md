---
id: 01JEV000000000000000000003
title: Atlas Sensor Hub Deployment
type: runbook
created: 2024-02-03T08:30:00Z
updated: 2025-04-02T13:15:00Z
tags: [atlas, deployment, containers]
---
# Atlas Sensor Hub Deployment

## Current production shape

Release **2.4.1** runs as containers on one small virtual machine. Caddy is the only public process
and terminates TLS on port 443. It forwards API traffic to `atlas-api` on internal port 8080 and
dashboard traffic to `atlas-dashboard` on internal port 3000. Neither application port is exposed
directly.

## Deployment procedure

1. Build an immutable image tagged with the release number and commit hash.
2. Apply database migrations in the staging environment.
3. Pull the same image on production and run the smoke checks.
4. Confirm `/healthz`, one synthetic ingestion batch, and dashboard freshness.
5. Retain the previous image tag until the next successful backup.

## Rollback

If health checks fail, restore the previous image tag and restart the two application containers.
Database migrations must be backward compatible for one release so image rollback does not require
an immediate database restore.

