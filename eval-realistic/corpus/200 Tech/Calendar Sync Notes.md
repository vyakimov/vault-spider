---
updated: 2026-06-09T11:00:00
id: 01M6V00000000000000000000N
created: 2026-05-09T10:00:00
---
# Calendar Sync Notes

Keeping a personal calendar in sync across devices without a cloud account.

## The Setup
My calendar lives as an ICS file in LordByron. Each device syncs it via rsync on a daily cron job. The calendar app on phone and laptop reads from the local copy. When I create an event, it goes into the local copy first, and the next sync pushes it everywhere. There's no conflict resolution (I just don't create overlapping events), but for solo organizing it works fine.

## Limitations and Why They're Okay
There's a lag of up to 24 hours for events created on the phone to appear on the laptop—this would be unacceptable for collaborative calendars, but I'm the only person using it. I also manually handle recurring events (no complex repeat rules). This keeps the ICS file simple and readable. For shared events (coordination with others), I use a separate Google Calendar and just maintain two calendars mentally. It's a split solution but it works: personal stuff is private and local, shared events live in Google.
