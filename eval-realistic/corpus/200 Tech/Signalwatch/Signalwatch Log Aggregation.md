---
updated: 2026-04-03T11:22:00
id: 01M6K00000000000000000000A
created: 2026-03-03T10:14:00
---
# Signalwatch Log Aggregation

I ship journald logs from each host in the tailnet into a small Loki instance running on the Bramble VPS. This gives me a central place to search and correlate events across machines.

## Collection
The Promtail agent runs on each host and tails journald, then forwards logs with timestamp and hostname labels. I keep only 7 days of logs locally to avoid filling the Bramble disk. High-volume services like DNS queries are sampled down to every 10th entry.

## Queries
I mostly search when debugging an incident. Recent queries: "process=postgres status=error" and "hostname=Blackbird AND message=*scrub*" to check on backup job runs. Loki's label-based index makes these lookups instant.
