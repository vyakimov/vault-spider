---
tags:
  - homelab
  - photos
updated: 2026-01-04T10:46:00
id: 01M6P000000000000000000007
created: 2026-06-01T09:02:00
---
Switched to NVIDIA's GPU-accelerated thumbnail generation and shaved 18 hours off a full re-index. The bottleneck was CPU—a single core could only encode ~3 thumbnails/second. GPU does ~60/second on the same workload. Needed driver version 555+ (earlier versions had a NVENC firmware bug that crashed midway through large batches). The process still runs in the off-peak hours, but now completes before morning instead of dragging into the next day.
