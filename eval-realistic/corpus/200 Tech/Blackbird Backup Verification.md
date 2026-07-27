---
updated: 2026-06-19T11:18:00
id: 01M6Q000000000000000000007
created: 2026-05-19T10:06:00
---
# Blackbird Backup Verification

A monthly scrub job that verifies backup integrity and surfaces failures.

## Process
Every first Sunday of the month, a cron job kicks off a `zfs scrub` on Blackbird's backup pools. The scrub takes about 6 hours and checks every block for corruption. Results are logged to the Loki instance and I get a Signal notification of any errors found.

## Follow-up
If a corruption is found, I manually investigate whether it's a media defect (bad sector) or a transient bit flip. Media defects trigger a disk replacement; transient errors are retried. In 3 years, I've had 2 media defects and 4 transient errors—an acceptable failure rate.
