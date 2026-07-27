---
updated: 2026-07-05T11:02:00
id: 01M6V000000000000000000043
created: 2026-06-05T10:34:00
---
# Old NAS Decommission Notes

A record of safely retiring and wiping the Blackbird NAS unit that preceded the newer LordByron, including data migration steps.

## Migration Workflow
Before decommissioning, I cloned the critical volumes to LordByron over the network—took about 18 hours at night to avoid disrupting active backups. Once verified that all data replicated correctly and the new NAS had a full backup cycle, I logged into the Blackbird admin panel and initiated a factory reset from the web UI. The drive wipe process ran for several hours, removing all configuration and user data.

## Decommissioning
After the wipe, I powered down the Blackbird and removed it from the rack. Kept the drives separate pending a secure destruction method—they'll either be wiped a second time or physically destroyed. Updated the rack diagram and inventory list to remove the old unit. LordByron is handling the load perfectly, and retiring the older machine frees up power supply capacity and cooling airflow in the rack.
