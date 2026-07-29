---
updated: 2026-01-04T11:05:00
id: 01M6V00000000000000000000G
created: 2026-07-04T10:25:00
---
# Phone Backup Strategy

How phone photos and messages get backed up now that Cassowary exists.

## The Setup
My phone syncs photos automatically to a folder on LordByron using a direct SSH tunnel—nothing goes through a cloud service. Messages stay on the phone (they're not sensitive, just low-value), but I have a monthly export of important conversations to PDF for archive. The SSH tunnel runs over the tailnet, so it's encrypted end-to-end and only accessible from inside the home network.

## Why This Matters
I used to use iCloud for photos and then realized I was paying for storage I didn't need. Local sync to a NAS is cheaper long-term and doesn't depend on Apple's infrastructure decisions. Photos are organized by year/month automatically via a script that reads their timestamps. Messages are kept locally on the phone, but important ones (project notes, decisions, contact info) get copy-pasted into the vault or an archive file. It's a hybrid approach that balances convenience and local control.
