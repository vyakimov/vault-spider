---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000003
created: 2026-01-30T14:17:26
---
a [[technote]] on git worktrees

`git worktree add ../repo-review origin/main` checks out a second working copy sharing the same
`.git`, so you can review a branch while your build keeps running in the first one.

`git worktree list` shows them, `git worktree remove ../repo-review` cleans up. Prune stale ones
with `git worktree prune`.
