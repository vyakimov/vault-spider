---
tags:
  - homelab
  - photos
updated: 2026-06-26T10:02:00
id: 01M6P000000000000000000003
created: 2026-02-23T09:34:00
---
# Cassowary Storage Layout

Original files live on [[LordByron]]'s `photos-originals` volume at `/mnt/storage/cassowary/raw`, organized by import date (year/month/day). Thumbnails and intermediate crops get written to a separate `photos-cache` volume so regeneration doesn't touch the archive.

## Volume Mapping

`photos-originals` is the RAID-6 shelf on the NAS — large but slow. `photos-cache` is an SSD pool that can absorb the hammer of 50,000 thumbnails re-encoding without starving other workloads. The web app never touches raw files directly.

## Symlink Strategy

The indexing daemon maintains a flat symlink tree at `/mnt/indexes/cassowary-by-date/` for rapid sequential walks during batch operations. If I regenerate thumbnails or rebuild the face index, the daemon updates this tree without re-cataloging.
