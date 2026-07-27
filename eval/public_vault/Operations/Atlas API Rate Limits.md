---
id: 01JEV000000000000000000144
title: Atlas API Rate Limits
type: reference
created: 2025-09-18T09:00:00Z
updated: 2026-03-23T12:00:00Z
tags: [atlas, operations]
---
# Atlas API Rate Limits

## Harbor Ingestion API

The Harbor API is the primary interface through which Cedar gateway units submit sensor batches for storage in PostgreSQL.

**Per-Device Rate Limits**
- Sustained: 600 requests per hour per Cedar device (10 requests per minute)
- Burst: 30 requests per minute (short-term spikes tolerated)
- Batch size: 100–500 sensor readings per request (45–225 KB uncompressed)
- Timeout: 10 second request timeout; Harbor retries with exponential backoff

**Aggregate Capacity**
- Harbor server can handle ~10,000 requests per hour (all devices combined)
- Concurrent connection limit: 50 active connections

**Error Responses**
- 429 (Too Many Requests): Rate limit exceeded; Cedar should back off exponentially
- 503 (Service Unavailable): Harbor is overloaded or PostgreSQL is unavailable
- 400 (Bad Request): Batch format validation error; inspect [[Atlas Data Quality Checks]] rules

## Dashboard Query API

The dashboard provides read-only query endpoints for fetching summarized sensor data.

**Public Endpoints** (no authentication)
- Limit: 1,000 requests per hour (per IP address)
- Examples: `/api/stations/latest`, `/api/readings/daily`
- Response caching: 5 minutes at client/CDN level

**Authenticated Endpoints** (API key required)
- Limit: 10,000 requests per hour (per API key)
- Examples: `/api/admin/logs`, `/api/debug/query-stats`
- Used by: Internal monitoring, automated health checks

## Rate Limit Recovery

When Cedar receives a 429 response from Harbor:
1. Pause batch transmission for 60 seconds
2. Retry with single batch (not bulk submission)
3. If still rejected after 3 retries, local queue backlog grows; escalate to on-call engineer

Recovery confirmation procedures are documented in [[Atlas Recovery Drill 2025-06]], which tests this failure scenario and validates the queuing workflow.

## Monitoring and Alerts

Rate limit exceedances are logged to the monitoring system and trigger alerts when:
- Any single Cedar device exceeds burst limit 3 times in an hour
- Harbor aggregate utilization exceeds 8,000 requests/hour sustained for >10 minutes
- Dashboard 429 responses exceed 5% of all requests in a 1-hour window

See [[Atlas Monitoring Alert Rules]] for alert definitions and escalation procedures.

## Related notes

- [[Atlas Recovery Drill 2025-06]]
- [[Atlas Monitoring Alert Rules]]
