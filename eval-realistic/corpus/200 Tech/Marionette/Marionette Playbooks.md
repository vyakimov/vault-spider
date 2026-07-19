---
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000008
created: 2026-03-19T12:08:40
---
# Marionette Playbooks

A [[Marionette]] note on playbook conventions.

A playbook is a markdown file under `~/.marionette/playbooks/` with frontmatter (`name`,
`triggers`, `requires`) and a body of numbered steps the agent follows. Rules that keep them
maintainable:

- One playbook = one outcome. "Morning digest" and "file the scans" are two playbooks.
- Steps reference tools by name, never by shell string — the allowlist stays the single source
  of what can run.
- A playbook that needs a decision mid-way should say *ask*, not guess.
- Version them in git like everything else in the workspace.

Naming: verb-first, lowercase, dashes (`file-the-scans.md`, `morning-digest.md`).
