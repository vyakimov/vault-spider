---
tags:
  - homelab
updated: 2026-06-21T10:53:00
id: 01M6D000000000000000000006
created: 2026-02-18T09:01:00
---
Tried extending the OCR pipeline to handle handwritten notes by tuning a separate handwriting model. The idea was to scan handwritten annotations and grocery lists, not just printed mail. The model worked okay on clean, formal handwriting but struggled with casual cursive and abbreviations. After two weeks of tweaking training data and hyperparameters, accuracy plateaued at ~75% on my own handwriting, which wasn't good enough to be useful. Archived the experiment and went back to printed-text-only OCR. The printed-mail recognition works so well (~96%) that the gap feels painful, and the code was adding unmaintainable complexity.
