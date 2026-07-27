---
updated: 2026-04-03T16:12:00
id: 01M6E000000000000000000167
created: 2026-03-01T09:48:00
---
`./main -m model.gguf -p "prompt" -n 512` runs inference on quantized model. GGUF format compresses weights ~4x; CPU inference on 7B-13B models feasible with 16GB RAM. OpenBLAS or CUDA acceleration flags speed output 3-5x.
