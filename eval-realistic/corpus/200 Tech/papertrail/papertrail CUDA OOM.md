---
updated: 2026-06-02T08:58:44
id: 01M6D000000000000000000003
created: 2026-05-05T17:26:58
---
a [[papertrail]] note on the A3 OOM

> [!SUMMARY] TL;DR
> Full-page A3 scans at 600dpi OOM the 8GB GPU during PaddleOCR detection. Fix: **tile the page
> into overlapping quarters and run detection per tile at fp16**, then merge boxes. Not a driver
> problem — the same batch runs fine on the same driver with tiling on.

The failing case: `RuntimeError: CUDA out of memory` on detection for anything scanned at A3
600dpi. A4 at 600dpi is fine, A3 at 300dpi is fine.

What fixed it:

1. Tile into 4 overlapping quadrants (10% overlap so boxes crossing the seam survive).
2. Run detection at fp16 — halves memory, no measurable accuracy change on this corpus.
3. Merge boxes with IoU dedupe across the overlap strips.

Ruled out: driver/CUDA version (same failure on two driver versions; and tiling fixes it on
both), other processes holding VRAM (nvidia-smi clean).

Recognition never OOMs — it's the detection stage that scales with page pixels.
