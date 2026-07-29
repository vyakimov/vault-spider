---
id: 01JEV000000000000000000139
title: Atlas Monitoring Alert Rules
type: reference
created: 2024-04-13T09:00:00Z
updated: 2024-07-18T12:00:00Z
tags: [atlas, operations]
---
# Atlas Monitoring Alert Rules

## Distinction from Telemetry Runbook

This document defines the **threshold rules** that trigger alerts in the monitoring system. See [[Atlas Telemetry Runbook]] for the corresponding **triage and recovery steps** that operators follow after receiving an alert.

## Cedar Gateway Alerts

**Batch Processing Lag**
- Rule: Alert if >100 batches queued locally for >30 minutes
- Severity: Medium (indicates Harbor API latency or Cedar network issue)
- Action: On-call engineer verifies Harbor API health and Cedar cellular connection

**Local Queue Capacity Warning**
- Rule: Alert at 50% queue fill, critical at 80%
- Threshold: Cedar unit has ~5000 batch slots; alert at 2500, critical at 4000
- Severity: Critical (risk of data loss if queue fills completely)
- Action: Immediate escalation; may require manual batch flushing

**Firmware Age**
- Rule: Alert if Cedar firmware is >6 months old
- Reason: Security patches and performance improvements released regularly
- Severity: Low (informational; does not require immediate action)

## Harbor API Alerts

**Ingestion Error Rate**
- Rule: Alert if >5% of batches are rejected (validation failures)
- Threshold: Calculated over 10-minute rolling window
- Severity: High (indicates data quality or API integration issues)
- Action: Check [[Atlas Data Quality Checks]] rules; review Cedar sensor status

**API Response Time**
- Rule: Alert if p95 latency exceeds 2 seconds
- Severity: Medium (degrades Cedar batch throughput)
- Action: Check database connection pool (see [[Atlas Cost Review 2024]] for historical performance baselines)

## PostgreSQL Database Alerts

**Disk Usage**
- Rule: Warning at 75% usage, critical at 90%
- Severity: Critical at 90% (no headroom for growth)
- Action: Trigger [[Atlas Storage Capacity Planning]] assessment; may require emergency volume expansion

**Connection Pool Exhaustion**
- Rule: Alert if >90% of max connections are in-use for >5 minutes
- Severity: High (new queries will be rejected)
- Action: Review query logs; scale connection limit if under [[Atlas Change Management Process]]

## Dashboard Alerts

**Application Health**
- Rule: Alert if dashboard process exits or fails to respond to health check
- Severity: Critical
- Action: Immediate restart; if recurrence, review recent deployments

**Query Timeout**
- Rule: Alert if >10% of dashboard queries timeout in a 1-hour window
- Severity: Medium (user-facing degradation)
- Action: Analyze slow-query logs; optimize common dashboard queries

All alerts are escalated according to [[Atlas Cost Review 2024]] on-call procedures and documented in the incident tracking system.
