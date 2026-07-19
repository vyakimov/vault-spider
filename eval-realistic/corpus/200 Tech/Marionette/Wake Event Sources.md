---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000002
created: 2026-04-05T13:47:26
---
A [[Marionette]] note. The catalogue of wake event sources — see [[Cron vs Wake Events]] for
when to use which.

- `file` — a path matched a glob (the papertrail hot folder uses this)
- `imap` — new mail matching a filter
- `webhook` — HTTP POST to the gateway's events endpoint
- `signal` — inbound message on an allowlisted chat
- `timer` — one-shot delay, for "remind me in 20 minutes" flows

Each source attaches its payload to the waking session, so the playbook starts with the reason
in hand instead of polling for it.
