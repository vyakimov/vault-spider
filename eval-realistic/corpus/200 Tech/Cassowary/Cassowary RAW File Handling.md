---
updated: 2026-04-10T11:39:00
id: 01M6P000000000000000000009
created: 2026-03-10T10:03:00
---
# Cassowary RAW File Handling

I decided to store RAW files alongside JPEGs instead of converting them on import. It's more disk-intensive but gives me archival flexibility and lets me re-process at higher quality later.

## Storage
For each JPEG, I store the corresponding CR3 raw file (my camera is Canon). They're deduplicated by hash to avoid storing identical raws twice. The NAS has enough space for about 2 years of my current capture rate.

## Tradeoffs
Conversion on import would be faster and cheaper in terms of disk, but would lock me into my current processing pipeline forever. Keeping both formats means I can experiment with different presets in Lightroom without re-downloading original files from the camera.
