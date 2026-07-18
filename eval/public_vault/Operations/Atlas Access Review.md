---
id: 01JEV000000000000000000011
title: Atlas Access Review
type: policy
created: 2024-05-06T10:00:00Z
updated: 2025-04-04T09:30:00Z
tags: [atlas, security, access]
---
# Atlas Access Review

## Principles

Harbor uses a dedicated database service account with no permission to create roles. The dashboard
has read-only access to summarized tables. Cedar authenticates with a gateway-specific credential
that can submit batches but cannot query historical data.

## Review cadence

Service credentials and operator roles are reviewed quarterly. Unused credentials are disabled
before deletion, and every rotation is tested with a synthetic batch. The review records role names
and outcomes, not personal names.

## Telemetry

Authentication logs retain service identity, result, and timestamp for 30 days. They do not record
request payloads or sensor readings.

