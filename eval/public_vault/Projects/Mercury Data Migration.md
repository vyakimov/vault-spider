---
id: 01JEV000000000000000000020
title: Mercury Data Migration
aliases: [Project Mercury]
type: project
created: 2024-08-12T09:00:00Z
updated: 2025-02-28T16:00:00Z
tags: [mercury, migration, data-engineering]
---
# Mercury Data Migration

Mercury is the codename for a fictional archive migration, not the planet. The project converts
1.8 million historical CSV rows into partitioned Parquet files while preserving the source archive.

## Validation

Each output partition records its source filenames, row count, minimum and maximum event time, and
SHA-256 checksum. The migration is accepted only when total row counts match and every source row
maps to exactly one output row.

## Rollout

The new reader runs in shadow mode for two weeks. During that period, sampled queries execute
against both formats and compare normalized results before Parquet becomes authoritative.

