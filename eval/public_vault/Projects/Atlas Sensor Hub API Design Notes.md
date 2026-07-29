---
id: 01JEV000000000000000000171
title: Atlas Sensor Hub API Design Notes
type: note
created: 2025-01-10T09:00:00Z
updated: 2025-04-15T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub API Design Notes

## Request Schema Evolution

Initial API proposals called for station-level message aggregation with flattened sensor arrays. Changed approach to hierarchical sensor grouping with per-sensor timestamps, enabling more granular filtering and query optimization during storage. Request payload size reduced by 18% through selective field compression for repetitive metadata.

## Batch Delivery Considerations

HTTP POST batching simplified client logic but created waterfall dependencies if any single message in a batch failed validation. Resolved by implementing partial batch acceptance: valid messages are committed while invalid ones return detailed error feedback for retry. Clients can now implement exponential backoff per-message rather than per-batch.

## Authentication and Rate Limiting

Considered mutual TLS for gateway authentication; chose HMAC-SHA256 signatures on request bodies with per-gateway rate limits instead. Signature approach eases operational debugging and allows key rotation without certificate authority coordination. Rate limits configured per region based on expected load profiles.

## Schema Versioning Strategy

Versioned APIs through accept-version headers rather than URL paths. Allows backward-compatible changes to be transparent to clients while supporting server-side deprecation of legacy versions on a documented timeline.
