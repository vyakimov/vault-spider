---
id: 01JEV000000000000000000005
title: Atlas Project Glossary
aliases: [Atlas Terms]
type: reference
created: 2024-01-12T09:15:00Z
updated: 2025-02-20T12:30:00Z
tags: [atlas, glossary]
---
# Atlas Project Glossary

## Cedar

The field gateway that receives LoRaWAN sensor readings, writes them to a durable SQLite queue, and
forwards acknowledged HTTPS batches. “Gateway” and “Cedar” refer to the same component.

## Harbor

The ingestion API that validates batches and writes accepted readings to PostgreSQL. “Harbor API”
and “ingestion service” refer to the same component.

## Beacon

The daily report summarizing data completeness, sensor health, rainfall, and notable gaps.

## Station

A named group of sensors at one sampling location. The public corpus uses fictional station names
only.

