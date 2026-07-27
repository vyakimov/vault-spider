---
updated: 2026-01-14T17:19:00
id: 01M6E000000000000000000178
created: 2026-07-12T20:11:00
---
Reciprocal rank fusion (RRF): `score = 1/(60 + rank)` for each system, sum. Weights can be tuned (e.g., 0.6 embeddings + 0.4 BM25). Learning-to-rank (LambdaMART) on labeled data beats manual tuning; cold-start: equal weights or 60/40 split.
