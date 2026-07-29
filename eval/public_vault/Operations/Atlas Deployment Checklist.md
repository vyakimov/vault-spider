---
id: 01JEV000000000000000000149
title: Atlas Deployment Checklist
type: checklist
created: 2024-05-23T09:00:00Z
updated: 2025-08-02T12:00:00Z
tags: [atlas, operations]
---
# Atlas Deployment Checklist

## Pre-Deployment Verification

- [ ] Cedar firmware version is signed and authenticated against the release manifest.
- [ ] Harbor API deployment package includes all dependencies and configuration bundles.
- [ ] Code review sign-off is documented from at least two reviewers.
- [ ] Staging deployment has passed smoke tests (ingestion pipeline, API health checks, dashboard data refresh).
- [ ] Rollback package from the previous version is staged and verified readable.
- [ ] Stakeholders (field site lead, Harbor ops, dashboard team) have been notified of the planned window.
- [ ] Deployment window has been scheduled outside peak ingestion hours (avoid 07:00-09:00 and 17:00-19:00 UTC).
- [ ] Database has been backed up within the last 4 hours.

## During Deployment

- [ ] Harbor API service stops cleanly and existing requests drain within 60 seconds.
- [ ] Cedar instances at all sites report the new version hash within 10 minutes of update.
- [ ] Initial data ingestion batches are logged and inspected for parsing errors.
- [ ] Dashboard connectivity is tested and at least one sensor is confirmed reading on the display.
- [ ] Operator on duty is available for immediate escalation throughout the deployment window.

## Post-Deployment

- [ ] All Cedar nodes confirm version consistency check passes.
- [ ] Harbor logs show zero request rejections for 30 minutes.
- [ ] Dashboard data freshness indicator shows green (last update within the expected interval).
- [ ] Alerts related to [[Atlas Sensor Calibration Log 2025]] ingestion status show normal operating ranges.
- [ ] Deployment completion is documented with version hash, duration, and any rollback events.

## Rollback Triggers

Abort immediately if: Harbor API fails to start, Cedar firmware checksum validation fails at any site, or dashboard fails to query data for more than 5 minutes post-deployment. In these cases, execute the staged rollback package and notify the lead architect.
