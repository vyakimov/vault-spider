---
id: 01JEV000000000000000000099
title: Backup Internet Failover Test
aliases: []
type: log
created: 2025-09-18T09:00:00Z
updated: 2026-03-23T12:00:00Z
tags: [infrastructure, networking]
---
# Backup Internet Failover Test

## Quarterly Failover Exercise Protocol

Backup internet connectivity via the cellular modem is tested once per quarter to verify that automatic failover activates correctly when the primary fiber link becomes unavailable. Testing is scheduled during low-traffic periods (typically early morning) to minimize impact on ongoing field observations.

## Test Procedure and Success Criteria

**Test setup:**
1. Schedule the test at least 72 hours in advance to notify research teams
2. Verify cellular modem is powered, SIM cards are active, and backhaul VLANs are configured
3. Verify primary firewall failover settings (automatic WAN switching enabled)
4. Confirm monitoring dashboard is capturing real-time metrics

**Execution steps:**
- At T+0: Disconnect the primary fiber interface from the main switch (simulating complete link loss)
- T+5: Verify that DNS queries resolve using cellular modem gateway
- T+10: Perform bandwidth test (expect 40–60 Mbps download, 5–15 Mbps upload)
- T+15: Check latency to remote site gateways (must stay <150 ms for stable tunnel)
- T+30: Reconnect primary link; verify automatic failback occurs and rebalance traffic
- T+45: Complete full regression test (all sites reachable, no packet loss)

**Success criteria:**
- Failover activation time: ≤60 seconds from primary link loss to first packet on cellular
- Cellular link stability: no packet loss during 30-minute sustained load test
- Failback convergence: traffic must revert to primary link within 5 minutes of reconnection
- DNS resolution: <200 ms response time on all queries during cellular active period

## Historical Test Results

| Date | Duration | Primary to Cellular | Cellular to Primary | Bandwidth | Latency | Result |
|------|----------|-------------------|-------------------|-----------|---------|--------|
| 2026-03-15 | 47 min | 23 sec | 3 min 12 sec | 52 Mbps | 124 ms | PASS |
| 2025-12-08 | 52 min | 31 sec | 4 min 45 sec | 48 Mbps | 118 ms | PASS |
| 2025-09-22 | 38 min | 18 sec | 2 min 28 sec | 61 Mbps | 98 ms | PASS |
| 2025-06-14 | 41 min | 26 sec | 3 min 33 sec | 54 Mbps | 112 ms | PASS |

All quarterly tests since Q3 2025 have succeeded without issues. Failover timing has gradually improved due to firmware optimizations in the Cradlepoint modem (version updates in 2025).

## Related Infrastructure Dependencies

Failover testing must coordinate with [[Site Power Outage Log 2024|power system testing]] to avoid concurrent maintenance windows. Generator activation is not required for failover testing since the UPS battery bank provides sufficient runtime for the 1-hour test period.

---
**Next scheduled test:** June 2026 (Q2 annual schedule)
