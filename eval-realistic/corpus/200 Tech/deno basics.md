---
updated: 2026-05-21T12:34:00
id: 01M6E000000000000000000133
created: 2026-04-19T11:26:00
---
`deno run --allow-read script.ts` runs TypeScript directly without a build step. Caches deps in `DENO_DIR`, no package.json. Lock file: `deno cache --lock=lock.json --lock-write` after adding imports.
