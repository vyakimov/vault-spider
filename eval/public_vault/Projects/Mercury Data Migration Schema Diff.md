---
id: 01JEV000000000000000000209
title: Mercury Data Migration Schema Diff
type: reference
created: 2025-03-22T09:00:00Z
updated: 2026-06-01T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Schema Diff

## Field-Level Mapping

The CSV schema contains 34 columns; the Parquet schema consolidates into 31 fields through normalization:

- `timestamp` (CSV: separate date and time columns) → unified ISO 8601 timestamp
- `sensor_id` (CSV: integer) → `sensor_id` (Parquet: string with prefix for backward compatibility)
- `reading_value` (CSV) → `value_float64` (Parquet: typed floating-point)
- `status` flag now includes enum validation (VALID, QUESTIONABLE, ERROR)

## Data Type Changes

CSV decimal precision for readings stored as text; Parquet uses float64 with precision validation during transformation. Timestamp resolution upgraded from minute-level to millisecond-level. Latitude/longitude fields expanded from 6-decimal places (11.1cm precision) to 8-decimal places (1.1cm precision) to support future spatial analytics.

## New Fields in Parquet Schema

- `ingestion_batch_id`: Links records to source transmission batch
- `transformation_version`: Tracks which migration pipeline version processed the record
- `data_quality_score`: Ranges 0-100, summarizes sensor health signals

## Deprecated Fields

Four CSV columns are omitted from Parquet: `legacy_device_code` (superseded by sensor_id), `manual_override_flag` (no longer used), `external_reference` (documentation only), `batch_checksum` (implicit in partition structure).

## Migration Context

See [[Atlas Project Charter]] for strategic rationale behind columnar migration. Field mapping decisions balanced backward compatibility with analytical efficiency.
