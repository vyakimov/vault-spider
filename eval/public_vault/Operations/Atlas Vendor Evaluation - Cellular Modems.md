---
id: 01JEV000000000000000000150
title: Atlas Vendor Evaluation - Cellular Modems
type: evaluation
created: 2025-06-24T09:00:00Z
updated: 2026-09-03T12:00:00Z
tags: [atlas, operations]
---
# Atlas Vendor Evaluation - Cellular Modems

## Candidates Evaluated

Three vendors were selected for evaluation as potential Cedar failover modems for sites with unreliable wired connectivity:

- **ModemCorp 5G Gateway**: Industrial-grade cellular modem with dual SIM slots, -40°C to 70°C operating range, rated for 99.2% uptime. Retail cost $3,400 per unit. Configuration time estimated at 4 hours per site.
- **TelecLink Rugged LTE**: Purpose-built for remote telemetry, single SIM, -20°C to 60°C range, 99.8% uptime SLA but on a regional carrier only. Cost $1,850 per unit, 2.5-hour configuration.
- **NetLinx Industrial 4G/5G Hybrid**: Dual connectivity stack, -30°C to 75°C range, 99.5% uptime, adaptive band selection. Cost $4,200 per unit, 6-hour setup including antenna tuning.

## Testing Results

Field testing was conducted at three remote sites over 60 days. ModemCorp achieved 99.1% uptime with 87ms average latency to Harbor ingestion endpoints. TelecLink met its SLA but was limited to LTE speeds (max 24 Mbps downlink); sufficient for typical 2MB batches but marginal during peak ingestion windows. NetLinx exceeded expectations with 99.87% uptime and 42ms latency, supporting full 5G throughput.

Failover detection and Cedar reconnection latency averaged 18 seconds across all candidates when wired connectivity dropped. ModemCorp showed the most stable failover behavior; TelecLink occasionally required manual reconnection prompts.

## Recommendation and Next Steps

NetLinx is recommended despite higher cost because the latency and throughput advantages support reliable Cedar batch submission and minimize the window where [[Atlas Data Export Procedure]] queries might experience unavailability. Budget approval is pending for Q4 2025 deployment at the five most remote sites. Contracts will include extended warranties covering salt-spray corrosion at coastal installations.
