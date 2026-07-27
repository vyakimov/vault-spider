---
id: 01JEV000000000000000000130
title: Atlas Firmware Rollback Procedure
type: procedure
created: 2025-04-04T09:00:00Z
updated: 2025-07-09T12:00:00Z
tags: [atlas, operations]
---
# Atlas Firmware Rollback Procedure

## Overview

This procedure describes how to revert the Cedar gateway firmware to a previously known-good version when a recent update introduces instability or connectivity loss. Use this only when the standard Cedar update procedure (documented separately) has failed to correct the issue.

## Pre-Rollback Verification

Before initiating rollback:
1. Confirm the Cedar unit is still reachable over the local network (ping the gateway's IP address)
2. Check the field technician's radio contact with the site—ensure you can coordinate actions in real time
3. Verify the previous firmware version number is documented in the version history file stored on the Cedar device

If the unit is fully unresponsive, proceed to the emergency recovery steps outlined in [[Atlas Handover Notes - New Technician]].

## Rollback Steps

1. SSH to the Cedar gateway using the staging environment credentials
2. Navigate to `/opt/cedar/firmware/archive/`
3. Identify the last known-good build (typically dated 1–2 weeks prior to the failed update)
4. Invoke the rollback script: `/opt/cedar/tools/revert.sh <version_tag>`
5. Monitor the console for boot completion (approximately 90 seconds)
6. Verify connectivity to Harbor ingestion API (test API endpoint: `/health`)
7. Clear any queued batches if the recovery indicates data corruption

## Post-Rollback Validation

After successful rollback, coordinate with [[Atlas Access Review]] to ensure component permissions are still properly scoped. Run the dashboard self-test to confirm normal viewing access is uninterrupted.

Document the rollback reason, timestamp, and final firmware version in the change log. Forward the incident summary to the vendor support contact (see [[Atlas Vendor Contact List]]).
