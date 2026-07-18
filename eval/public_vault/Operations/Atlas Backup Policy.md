---
id: 01JEV000000000000000000009
title: Atlas Backup Policy
type: policy
created: 2024-03-12T07:30:00Z
updated: 2025-01-20T10:00:00Z
tags: [atlas, backup, recovery]
---
# Atlas Backup Policy

## Schedule and retention

PostgreSQL receives an encrypted logical backup every night at 02:00 UTC. The backup store retains
30 daily copies and 12 month-end copies. Deployment configuration is backed up weekly. Original
sensor batches already reside in versioned object storage and are verified by checksum rather than
copied into the database backup.

## Recovery objectives

The recovery-point objective is 24 hours and the recovery-time objective is four hours. These are
service objectives, not guarantees that every individual reading is recent; Cedar may still hold a
newer offline queue.

## Verification

A successful upload is not sufficient. Every backup is checksum-verified, and one restore drill is
performed each quarter using an isolated database and a synthetic ingestion replay.

