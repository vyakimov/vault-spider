---
updated: 2026-03-19T10:00:00
id: 01M6E000000000000000000131
created: 2026-02-17T09:00:00
---
Add to `package.json`: `"volta": { "node": "18.16.0" }`. When you cd into the project, volta auto-selects that Node version. `volta pin node@18.16.0` updates it; works across teams without nvm config drift.
