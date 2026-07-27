---
id: 01JEV000000000000000000211
title: Mercury Data Migration Data Dictionary
type: reference
created: 2025-05-24T09:00:00Z
updated: 2026-08-03T12:00:00Z
tags: [mercury, project]
---
# Mercury Data Migration Data Dictionary

## Core Fields

**timestamp** (timestamp[ns]): ISO 8601 timestamp in UTC of reading acquisition. Converted from separate date/time columns in CSV. Precision: nanosecond (actual sensor resolution 1 minute). Range: 2017-01-01 through present.

**sensor_id** (string): Unique sensor identifier with format prefix_NNNNN (e.g., "ATL_00042"). Maintains backward compatibility with legacy integer sensor codes through prefix mapping. No nulls; uniqueness enforced by source systems.

**value_float64** (float): Measurement value in SI units (temperature in Kelvin, humidity in %, pressure in Pa). Range -100.0 to 200.0. Null values represent sensor malfunction or transmission loss; distinct from zero readings.

## Quality Indicators

**ingestion_batch_id** (string): UUID identifying the transmission batch containing this reading. Enables traceability to source transmission and associated metadata. Correlates with Cedar gateway queue operations.

**data_quality_score** (integer): Quality assessment 0-100. Factors include sensor age, calibration drift, signal strength, and data consistency checks. <50 indicates questionable data; >80 indicates reliable observation.

**transformation_version** (integer): Pipeline version that processed this record (1-7). Tracks schema evolution across migration phases. Enables auditing of transformation logic applied to specific records.

## Deprecated Columns

The following fields were present in CSV but omitted from Parquet: `legacy_device_code`, `manual_override_flag`, `external_reference`, `batch_checksum`. Records referencing these fields must use transformation_version metadata to infer historical context.
