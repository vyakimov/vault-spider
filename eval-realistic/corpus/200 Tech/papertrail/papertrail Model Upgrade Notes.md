---
updated: 2026-04-17T11:56:00
id: 01M6D00000000000000000000B
created: 2026-03-17T10:52:00
---
# papertrail Model Upgrade Notes

Notes from trying a newer OCR model release and whether it was worth switching.

## Test
I ran both Tesseract 4 and 5 on a batch of 50 test documents (mix of bills, contracts, handwritten notes) and compared accuracy. Version 5 improved character recognition from 94% to 96% overall, but struggled more with cursive writing than v4.

## Decision
I upgraded to v5 because the gains on printed text outweigh the handwriting regression (I rarely scan cursive). The upgrade required retraining on a small dataset of my own documents to tune the language model. Reprocessing the entire archive with the new model would take about 8 hours.
