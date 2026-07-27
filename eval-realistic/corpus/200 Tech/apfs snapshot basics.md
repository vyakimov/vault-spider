---
updated: 2026-01-10T11:27:00
id: 01M6E000000000000000000122
created: 2026-07-08T12:03:00
---
`tmutil localsnapshot` creates a Time Machine snapshot; `tmutil listlocalsnapshots /` lists them. Snapshots are read-only point-in-time copies using APFS COW. Delete old ones with `tmutil deletelocalsnapshots TIMESTAMP` if disk is full.
