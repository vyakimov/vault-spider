---
updated: 2026-06-12T11:01:00
id: 01M6A00000000000000000000G
created: 2026-05-12T10:17:00
---
# Marionette Context Window Notes

Notes on what gets trimmed from session context when a long-running Marionette conversation runs close to the token limit.

## Trimming Strategy
I keep the original task instruction and the most recent 5 exchanges verbatim. Earlier exchanges are summarized by the agent (a handoff to a cheaper model to save tokens). Tool results older than 30 messages are dropped unless they're error states.

## Tuning
Initially I kept everything and hit the limit frequently on multi-hour sessions. Now I aim to keep about 60% context headroom to leave room for large tool outputs (e.g., parsing a 50MB log file). For critical tasks, I manually save checkpoints and start a fresh session.
