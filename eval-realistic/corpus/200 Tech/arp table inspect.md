---
updated: 2026-06-04T14:18:00
id: 01M6E000000000000000000298
created: 2026-06-03T15:42:00
---
`arp -a` shows ARP table (IP to MAC mapping). Modern replacement: `ip neigh`. Use `arp -d 192.168.1.1` to flush an entry, then ping to refresh.
