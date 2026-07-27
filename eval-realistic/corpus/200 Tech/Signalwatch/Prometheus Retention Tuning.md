---
tags:
  - homelab
updated: 2026-05-08T10:44:00
id: 01M6K000000000000000000005
created: 2026-05-05T09:28:00
---
Prometheus filled the partition after running for 6 months with default retention (15 days). TSDB grows quickly with high cardinality metrics; I was scraping every label variant (host, interface, disk device) with 30-second intervals across 5 machines. Dropped retention to 7 days and reduced scrape interval to 60 seconds; at that cadence, disk usage is now stable at ~8GB. The tradeoff is I can't look back further than a week in dashboards, but for alerting that's fine. I created a separate cold-storage mount for long-term backups, but dumping and compressing the TSDB is slow enough that I haven't automated it yet. Monitoring disk usage on the Prometheus volume itself now with a dedicated alert (meta, I know).
