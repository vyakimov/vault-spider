---
updated: 2026-04-20T11:17:00
id: 01M6E000000000000000000132
created: 2026-03-18T10:13:00
---
`pnpm` uses hard links to a global store, making `node_modules` smaller and install faster. `npm` flattens deps (hoisting), which hides bugs. For monorepos, pnpm workspaces are cleaner; npm workspaces are clunkier.
