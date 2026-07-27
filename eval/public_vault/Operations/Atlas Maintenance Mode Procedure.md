---
id: 01JEV000000000000000000161
title: Atlas Maintenance Mode Procedure
type: procedure
created: 2024-08-09T09:00:00Z
updated: 2025-02-14T12:00:00Z
tags: [atlas, operations]
---
# Atlas Maintenance Mode Procedure

## Purpose and Scope

The dashboard enters maintenance mode during planned infrastructure updates, database migrations, or large-scale redeployments. In maintenance mode, users see a holding page indicating the system is temporarily offline, with an estimated return time. This procedure ensures clear communication and prevents accidental data corruption from queries during partially consistent states.

## Pre-Maintenance Checklist

- [ ] Scheduled window is communicated to all users at least 48 hours in advance.
- [ ] Harbor API will be operational (batches will continue to be ingested and queued for the dashboard).
- [ ] Cedar instances continue to operate normally; local buffering ensures no data loss.
- [ ] Stakeholders (field site leads, external data consumers) have been notified via email and Slack.
- [ ] On-call database administrator will monitor the procedure.
- [ ] Estimated maintenance duration is reasonable (target: under 2 hours for routine updates).

## Enabling Maintenance Mode

1. Log into the dashboard infrastructure as an administrator.
2. Locate the feature flag configuration file (typically in `/etc/atlas-dashboard/feature_flags.yaml`).
3. Set `maintenance_mode: true` and `maintenance_message: "System is undergoing scheduled maintenance. Expected return: [time]"`.
4. Restart the dashboard web service (or reload configuration; depends on deployment model).
5. Verify that users accessing the dashboard see the maintenance page (test with both desktop and mobile browsers).
6. Monitor Harbor API ingestion to confirm batches are being received and queued.

## During Maintenance

- Update database schema, apply patches, or perform infrastructure changes as planned.
- Monitor database logs for errors or warnings.
- Periodically verify that Harbor continues to accept batches (query the ingestion queue count).
- Keep the on-call DBA informed of progress; adjust estimated return time if needed.
- If maintenance takes longer than planned, issue an updated communication with new ETA.

## Exiting Maintenance Mode

1. Verify that all database changes have completed successfully.
2. Confirm that the dashboard application layer is fully deployed and responsive.
3. Test dashboard functionality with a sample query (e.g., verify that recent sensor readings are visible).
4. Set `maintenance_mode: false` in the feature flag configuration.
5. Reload configuration or restart the dashboard web service.
6. Clear browser caches (or wait for client-side caches to expire) to ensure users see the updated dashboard.
7. Monitor the dashboard for 30 minutes post-recovery to detect any new issues.

## Communication Template

**Pre-Maintenance (48+ hours before)**:
"Scheduled Maintenance Notification: The Atlas dashboard will be offline [DATE] [START TIME] - [END TIME] UTC for [brief reason]. Cedar field gateways and Harbor ingestion will continue operating normally. We apologize for the inconvenience."

**Post-Maintenance (within 30 minutes of return)**:
"Maintenance Complete: The Atlas dashboard has been restored and is fully operational. Thank you for your patience."

## Rollback Procedure

If a critical issue is discovered during maintenance (e.g., database migration failure), immediately disable maintenance mode and restart the dashboard to restore user access. If restoration is not possible, escalate to the system architect and prepare to restore from the previous database backup.

## Metrics and Logging

- Record the actual start and end times of maintenance.
- Log the reason for maintenance and any issues encountered.
- Track Harbor batch queue depth before, during, and after maintenance to ensure no batches are lost.
- Measure dashboard latency after re-entry to confirm performance is nominal.
