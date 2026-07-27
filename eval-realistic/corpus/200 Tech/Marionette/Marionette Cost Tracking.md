---
tags:
  - homelab
  - llm
updated: 2026-02-11T10:03:00
id: 01M6A00000000000000000000A
created: 2026-06-08T09:51:00
---
I keep a running tally of token usage by day in a simple SQLite schema (input_tokens, output_tokens, model, date). The cost calculator multiplies by the per-model rates and dumps a monthly report. July 2026 averaged about $12/day, mostly from longer reasoning traces on complex problems. I don't throttle or add artificial delays — the goal is just to stay aware of what's getting spent. If I see a runaway month (say, a daemon looping on failures), the logs make it easy to spot which conversations blew the budget.
