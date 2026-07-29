---
updated: 2026-02-14T11:41:00
id: 01M6V000000000000000000052
created: 2026-01-14T10:37:00
---
# Tailnet Device Naming Convention

A documented naming pattern for tailnet machines that keeps names memorable and organized as the network grows.

## Naming Scheme
Devices are named by category and purpose: `[type]-[name]-[role]`. Examples: `workstation-desk`, `server-lord-byron`, `vps-bramble`, `phone-primary`. This makes it easy to scan a device list and understand what each thing does without needing to look up documentation. Shorthand hostnames like `des`, `lby`, `bra` work for common machines. The role suffix clarifies if there's redundancy—`server-old-nas` versus `server-new-nas` during a migration.

## Guidelines
Keep names short but meaningful. Avoid numbers unless they're part of the product name. Use lowercase and hyphens only. When decommissioning a device, remove it cleanly rather than renaming it to "old-" to avoid confusion. This convention has scaled well as the tailnet grew from 3 to 15+ devices. New people joining the tailnet can understand the naming at a glance.
