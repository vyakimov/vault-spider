---
updated: 2026-06-02T09:05:20
id: 01M6H00000000000000000000A
created: 2026-04-20T17:14:29
---

A [[Larder]] implementation note on the barcode flow.

The phone camera feeds html5-qrcode in the browser — no native app. EAN-13 covers nearly
everything from the supermarket; the failures are produce bags and bakery items, which fall
back to the fuzzy name search.

Lookup order: local `products` table first, then the public product database, then manual
entry. Manual entries backfill the local table so the same item is never typed twice.

Torch button matters more than expected: pantry lighting is terrible.
