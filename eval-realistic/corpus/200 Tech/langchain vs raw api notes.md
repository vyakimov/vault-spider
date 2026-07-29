---
updated: 2026-07-06T19:03:00
id: 01M6E000000000000000000170
created: 2026-06-04T12:27:00
---
LangChain abstracts model/memory/retrieval chains but adds latency and dependency bloat. Raw API (anthropic.Anthropic()) is 10-20 lines for basic chat, full control, no opinionated middleware. Use LangChain for complex multi-step agents; direct API for straightforward RAG.
