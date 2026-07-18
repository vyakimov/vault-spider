---
id: 01JEV000000000000000000002
title: Atlas Sensor Hub Architecture
type: architecture
created: 2024-01-15T10:00:00Z
updated: 2025-02-20T12:00:00Z
tags: [atlas, sensors, architecture]
---
# Atlas Sensor Hub Architecture

## Data path

Field sensors transmit over LoRaWAN to the **Cedar gateway**. Cedar writes each reading to a local
SQLite queue before acknowledging it. The queue retains up to 72 hours of readings, exceeding the
project's 48-hour offline-operation target.

When a connection is available, Cedar sends compressed HTTPS batches to the **Harbor API**. Harbor
validates timestamps and sensor identifiers, writes accepted readings to PostgreSQL, and archives
the original batches in object storage. The dashboard reads summarized data from PostgreSQL rather
than querying sensors directly.

## Failure boundaries

A network outage stops forwarding but not local collection. An API outage causes Cedar to retry
with exponential backoff. A malformed reading is quarantined with a reason code so one bad sensor
does not reject the rest of a batch.

## Security boundary

Sensors cannot accept inbound internet connections. Cedar initiates all API traffic over HTTPS and
uses the split-tunnel network described in [[WireGuard Network - Current]].

