---
updated: 2026-04-24T11:13:00
id: 01M6R000000000000000000004
created: 2026-03-24T10:41:00
---
# Waystation Click Analytics

A minimal dashboard showing click counts and referrers per link.

## Dashboard
I built a simple Grafana dashboard that queries the clicks table and shows: (1) total clicks per link over time, (2) top referrers, (3) unique user agent counts. The dashboard is read-only and accessible only on the tailnet.

## Insights
The analytics are useful for understanding which shared links are actually being clicked. I've noticed docs links get more clicks in the morning, while casual share links peak in the evening. Nothing surprising, but nice to confirm hunches.
