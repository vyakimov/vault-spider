---
updated: 2026-03-28T15:55:00
id: 01M6E000000000000000000166
created: 2026-02-26T20:35:00
---
`ollama pull mistral` downloads model to ~/.ollama/models. `ollama run mistral "prompt"` streams response; expose on localhost:11434 for external API access. Quantized models (7B-13B) run on consumer GPUs with 8GB VRAM.
