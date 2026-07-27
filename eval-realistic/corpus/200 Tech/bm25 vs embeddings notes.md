---
updated: 2026-07-13T16:02:00
id: 01M6E000000000000000000177
created: 2026-06-11T19:58:00
---
BM25 (sparse, keyword-based) excels on exact-term queries (rare words, entities) but misses paraphrase. Embeddings catch semantic similarity but fail on rare/OOV terms. Hybrid (rrf or learned fusion) scores both, optimal for mixed workloads; 5-10% MRR gain.
