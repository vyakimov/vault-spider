---
updated: 2026-05-11T14:28:00
id: 01M6E000000000000000000175
created: 2026-04-09T17:32:00
---
`chromadb.Client().get_or_create_collection("name")` + `.add(documents=[], embeddings=[])` stores vectors. In-memory by default; persist with `chroma.Client(chroma.config.Settings(persist_directory="/path"))`. Metadata filtering on get/query; no native reranking.
