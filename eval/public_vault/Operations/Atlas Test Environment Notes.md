---
id: 01JEV000000000000000000156
title: Atlas Test Environment Notes
type: reference
created: 2025-03-04T09:00:00Z
updated: 2026-06-09T12:00:00Z
tags: [atlas, operations]
---
# Atlas Test Environment Notes

## Staging Environment Overview

The Atlas staging environment is a complete replica of production deployed on shared infrastructure in us-east-1. It consists of one simulated Cedar gateway instance (in a container, not deployed to a physical site), Harbor API running on a t3.medium EC2 instance, PostgreSQL 14.7 on a managed RDS instance (db.t3.small), and a dashboard instance served through CloudFront.

Network isolation is enforced via security groups; staging Cedar cannot reach production Harbor, and production clients cannot access staging infrastructure. Database is reset weekly from a production backup taken 1 week prior, providing realistic data volumes without exposing live data.

## Cedar Simulator Configuration

The Cedar simulator injects sensor readings at configurable frequency (default 1 reading per 30 seconds per sensor, 4 sensors total). Batch submission to Harbor occurs every 200 readings or every 5 minutes, whichever comes first. The simulator supports fault injection: network latency injection (0-500ms), packet loss (0-10%), connection timeouts, and database unavailability scenarios.

## Testing Workflows

**Functional Testing**: Developers deploy code changes to Harbor or the dashboard, Cedar simulator submits test batches, and dashboards verify correct visualization and database state. Average cycle time is 15 minutes from code push to verification.

**Load Testing**: Cedar simulator can scale to 10 concurrent instances, submitting 40 batches per minute total (simulating load equivalent to 8-10 physical field sites). Harbor API response times and database query latency are measured under sustained load.

**Failover Testing**: Harbor API can be manually taken offline to test Cedar local buffering and batch retry logic. Database connection failures can be simulated via RDS parameter group changes.

## Access and Credentials

Staging environment credentials are stored in AWS Secrets Manager. Read-only access is granted to all developers. Write access to Harbor or database configuration requires approval from the operations lead. SSH access to EC2 instances is restricted to on-call operations personnel.

## Maintenance and Data Lifecycle

The staging PostgreSQL database is reset every Sunday at 02:00 UTC. Staging Cedar simulator history is flushed weekly. Lingering test artifacts are cleaned up by an automated housekeeping job running Sundays at 03:00 UTC. Staging costs average $280/month for compute and storage.
