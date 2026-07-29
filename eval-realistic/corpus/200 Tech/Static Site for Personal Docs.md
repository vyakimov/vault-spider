---
updated: 2026-01-16T11:31:00
id: 01M6V000000000000000000002
created: 2026-07-16T10:47:00
---
# Static Site for Personal Docs

Publishing a small static site of reference docs, separate from this vault and not for sharing.

## The Motivation
My vault is full of personal notes—routines, configuration snippets, half-baked plans. Some of that is genuinely useful enough to revisit, but none of it is polished enough to share. A static site lets me render a curated subset (command references, setup instructions, deployment notes) without publishing the entire messy vault. It lives at a private domain only I know about.

## Build and Hosting
Hugo pulls markdown from a specific folder, generates HTML, and I rsync it to a bare metal server that's not exposed to the tailnet. The site has no backend, no database, no auth. If the server goes down, the docs are still in git. I update it maybe twice a month when a process changes enough to be worth documenting.
