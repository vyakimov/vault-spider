---
updated: 2026-06-26T11:35:00
id: 01M6R000000000000000000006
created: 2026-05-26T10:55:00
---
# Waystation QR Code Generation

Generating a QR code alongside each short link for print use.

## Feature
When I create a short link, Waystation generates a PNG QR code that encodes the shortened URL. I can embed this in documents or print it for a poster. The QR code is regenerated on demand but cached for 24 hours.

## Implementation
I use the `qrcode` Python library and cache PNGs in `/tmp` on Bramble. QR code size adjusts based on target URL length (longer URLs need more cells). Error correction is set to "M" (medium) to handle minor scanning imperfections.
