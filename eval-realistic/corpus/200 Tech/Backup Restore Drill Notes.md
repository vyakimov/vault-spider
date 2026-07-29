---
updated: 2026-01-20T11:47:00
id: 01M6V000000000000000000058
created: 2026-07-20T10:19:00
---
# Backup Restore Drill Notes

An annual practice restore from the offline USB backup to verify that recovery procedures actually work before they're needed in an emergency.

## Drill Procedure
I bring the backup disk into the house, connect it to a test machine, and decrypt it with the recovery passphrase (stored separately). Then I restore a subset of files—enough to verify the backup is readable and data integrity is sound. This process takes about an hour and has caught issues: once a checksum mismatched, once the passphrase was transcribed wrong. Without this drill, I wouldn't know if the backup was usable until it was too late.

## Results and Adjustments
After each drill I update notes on recovery time and any problems encountered. Last year's drill found that the backup drive was starting to fail—early warning that led me to clone it to a replacement drive before loss occurred. This year's drill went smoothly, data verified intact, recovery scripts executed without error. The cost of one hour annually is trivial compared to the confidence that I could actually recover my data if needed.
