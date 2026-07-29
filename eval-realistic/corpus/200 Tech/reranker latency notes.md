---
updated: 2026-04-10T13:11:00
id: 01M6E000000000000000000174
created: 2026-03-08T16:19:00
---
Cross-encoder reranking (cohere-rerank-english) adds 200-500ms per batch; only worth it if top-50 retrieval is noisy. Local jina-reranker on GPU is 2-3x faster than API; batch size 32 optimal. Skip reranking if embedding recall already >80%.
