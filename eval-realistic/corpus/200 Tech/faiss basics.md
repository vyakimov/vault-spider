---
updated: 2026-06-12T15:45:00
id: 01M6E000000000000000000176
created: 2026-05-10T18:45:00
---
`faiss.IndexFlatL2(dim)` creates a flat index; `.add(vectors)` / `.search(queries, k)` return nearest k neighbors. Flat index is slow for >1M vectors; use IVF+PQ (IndexIVFPQ) for 100M+ scale. GPU index 10-100x faster but requires CUDA.
