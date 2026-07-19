---
id: 01JEV000000000000000000030
title: Atlas Cost Review 2025
type: review
created: 2025-07-08T13:00:00Z
updated: 2025-07-08T13:00:00Z
tags: [atlas, operations, costs]
---
# Atlas Cost Review 2025

## Where the money goes

Hosting for the API and database is the single largest line, followed by object storage for
archived batches, then the LoRaWAN antenna site fee. Sensor batteries are noise in comparison.

## Trend

Storage grows slowly and predictably because summaries dominate long-term volume; the raw
archive is compressed and ages out of hot storage. Hosting has been flat for two years.

## Conclusions

No changes. The one watch item is object storage class fees: if the provider reprices cold
storage, revisit how long archived batches stay retrievable. Retention policy itself is a
product decision recorded in [[Atlas Decision Log]], not a cost lever to pull casually.
