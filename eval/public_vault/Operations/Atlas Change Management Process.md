---
id: 01JEV000000000000000000133
title: Atlas Change Management Process
type: procedure
created: 2024-07-07T09:00:00Z
updated: 2024-01-12T12:00:00Z
tags: [atlas, operations]
---
# Atlas Change Management Process

## Overview

All changes to Atlas production infrastructure (Cedar firmware updates, PostgreSQL configuration, Harbor API settings, and dashboard deployments) must follow this approval process before implementation. The goal is to minimize unplanned outages and ensure every change is documented and reversible.

## Change Classification

**Standard Changes** (require single approval):
- Routine security patches for third-party libraries
- Dashboard UI updates with no database schema changes
- Configuration parameter tuning within documented ranges

**Major Changes** (require manager approval + technical review):
- Cedar or Harbor firmware updates
- PostgreSQL schema modifications
- New sensor types or field deployments
- Changes affecting [[Atlas Incident Severity Levels]] classifications

**Emergency Changes** (require post-incident documentation):
- Rollback procedures when production is already down
- Hotfixes for critical security vulnerabilities
- Temporary workarounds pending full resolution

## Approval Workflow

1. Engineer submits change request with: description, estimated duration, rollback plan, and required downtime window
2. Technical reviewer (peer engineer) confirms rollback feasibility and test coverage
3. Manager approves window and escalation contact
4. Change is logged with date, implementer, approval chain, and outcome
5. Post-change verification is documented (see [[Service Port Registry]] for connectivity validation)

## Documentation

Each change must include a reason, affected systems, and measured outcomes (latency, availability, resource usage). This history informs future decisions about infrastructure scaling and vendor contract terms referenced in [[Atlas Incident Severity Levels]].

Minor failed changes (e.g., config syntax error caught during deployment) are still documented but may skip full post-mortem review.
