---
updated: 2026-03-03T18:06:00
id: 01M6E000000000000000000089
created: 2026-02-01T15:54:00
---
Add to `/etc/exports`: `/data *(rw,sync,no_subtree_check)`. Run `exportfs -a` to reload. Clients mount via `mount -t nfs server:/data /mnt/data`. Check exports with `showmount -e server`.
