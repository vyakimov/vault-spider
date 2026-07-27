---
updated: 2026-06-05T11:44:00
id: 01M6M00000000000000000000A
created: 2026-05-05T10:28:00
---
# Greenhouse Energy Monitoring

I added a smart plug with power monitoring to track how much juice the server rack is drawing. Helps me understand whether the cooling upgrades actually paid off.

## Measurement
The plug reports power consumption every 30 seconds to Home Assistant. I export the data to InfluxDB and graph it in Grafana. The baseline is around 420W idle, and it peaks at 670W during heavy backup runs or replication.

## Findings
The cooling fan I added in May shaved off 30W during sustained workloads by reducing CPU throttling. The total monthly cost of running the rack is roughly stable year-round despite seasonal ambient temperature changes, mostly because I use less compute in summer.
