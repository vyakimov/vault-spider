---
tags:
  - homelab
  - llm
updated: 2026-07-12T10:14:00
id: 01M6A00000000000000000000B
created: 2026-07-09T09:58:00
---
# Marionette vs Lantern Feature Comparison

Marionette and [[Lantern]] are different enough that direct feature parity isn't the goal; instead, each fills different niches in my homelab agent ecosystem.

## Feature Matrix

| Feature | Marionette | Lantern |
|---------|-----------|---------|
| Long-context reasoning | Yes | No (fixed 8k window) |
| Signal integration | Yes | No |
| Tool composition | Sequential only | Yes (parallel tools) |
| Web UI | Minimal (logs only) | Rich dashboard |
| On-device models | No (API-only) | Yes (Llama 3) |
| Multi-turn memory | 90-day retention | Session only |

Marionette is for heavyweight async tasks (long reports, complex tool orchestration). Lantern is for quick on-device queries without latency sensitivity.
