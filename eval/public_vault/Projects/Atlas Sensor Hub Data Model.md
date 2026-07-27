---
id: 01JEV000000000000000000175
title: Atlas Sensor Hub Data Model
type: reference
created: 2025-05-14T09:00:00Z
updated: 2026-08-19T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Hub Data Model

## Readings Table Schema

`readings` table stores raw sensor observations: station_id (foreign key), sensor_type (temperature, humidity, pressure), observed_value (numeric), unit_of_measure (°C, %, hPa), observation_timestamp (UTC), and insertion_timestamp (server-local time). Indexed on station_id and observation_timestamp for fast range queries. Partitioned monthly by observation_timestamp to support efficient archival.

## Summaries Table

`hourly_summaries` and `daily_summaries` tables compute min/max/mean across raw readings within hour and day boundaries. Computed asynchronously on a nightly batch process; back-filling new summaries for gaps due to reprocessing. Allows dashboard to render historical trends without scanning millions of raw rows.

## Device Metadata

`stations` table tracks network connectivity history, installed sensor complement, gateway hardware revision, and contact information for on-site personnel. `sensors` table records per-sensor configuration like measurement range, calibration constants, and last-maintenance date. Updates to these tables trigger re-computation of summaries for affected date ranges.

## Validation and Audit Trail

`data_imports` table logs each batch ingestion with source gateway identifier, message count, checksum, and acceptance status. Failed validations recorded with specific error detail to enable replay. Integration with [[Mercury Data Migration Vendor Notes]] validation patterns ensures data lineage transparency.
