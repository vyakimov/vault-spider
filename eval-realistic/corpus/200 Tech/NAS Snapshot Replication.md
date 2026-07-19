---
updated: 2026-06-02T08:54:02
id: 01M6B000000000000000000006
created: 2026-02-27T20:15:33
---

Snapshot schedule on [[LordByron]], a [[technote]]

Hourly snapshots of the main volume, keep **24 hourly and 30 daily**; monthly replication of the
latest daily to the offline USB disk in the drawer (rotate two disks, odd/even months).

`Storage & Snapshots -> Snapshot Manager -> Schedule` for the schedule; replication is a
`Snapshot Replica` job pointed at the USB target.

Restores: mount the snapshot read-only and copy out, don't roll the whole volume back unless the
volume itself is toast.

#finalised
