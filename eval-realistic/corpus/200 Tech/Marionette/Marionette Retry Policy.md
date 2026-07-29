---
updated: 2026-05-11T11:50:00
id: 01M6A00000000000000000000F
created: 2026-04-11T10:10:00
---
# Marionette Retry Policy

Notes on how failed tool calls are retried in Marionette playbooks, and when failures get surfaced to me instead of being silently retried.

## Automatic Retries
By default, a failed tool call retries once after a 5-second backoff. If the second attempt fails, the failure is logged but doesn't crash the playbook. Network errors (timeout, connection refused) retry; permission errors and type mismatches don't, since retrying those is pointless.

## Escalation
If a tool fails twice in a 10-minute window, I get a Signal notification. Critical playbooks (backups, security checks) have stricter rules—single failure triggers a notification. I review the notification within an hour and can manually retry or skip the step.
