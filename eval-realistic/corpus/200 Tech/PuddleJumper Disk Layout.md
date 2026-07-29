---
updated: 2026-01-28T10:21:00
id: 01M6B00000000000000000000C
created: 2026-03-26T09:57:00
tags:
  - homelab
  - hardware
---
`lsblk -o NAME,SIZE,MOUNTPOINT` shows: 500GB NVMe (/ and /var), 2TB SSD (/home), 4TB HDD (/archive). Partitions via `parted /dev/nvme0n1` with GPT; mounted in fstab by UUID from `blkid`. Archive drive is cold storage, mounted ro unless needed; verify with `mount | grep archive`.
