---
tags:
  - homelab
updated: 2026-02-16T10:12:00
id: 01M6M000000000000000000006
created: 2026-06-13T09:24:00
---
Home Assistant snapshots back up the entire config (automations, devices, history) nightly. Snapshots live on the local filesystem (PuddleJumper's `/opt/homeassistant/backups`), not synced to [[LordByron]]. This is separate from [[NAS Snapshot Replication]], which handles the VM's entire disk image. I keep 7 days of snapshots and occasionally restore one after a bad automation change. The snapshot size is about 150 MB each (mostly history database). No cloud upload; I manually grab one if I need to migrate the setup or debug a config problem offline.
