---
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000002
created: 2026-01-08T10:12:33
---
A [[technote]] on keeping Homebrew from rotting.

`brew autoremove` after uninstalling anything — orphaned deps pile up silently.
`brew doctor` complains a lot; the only warnings I act on are broken symlinks.
`brew leaves` shows what I actually asked for, everything else is deps.

Once a quarter: `brew update && brew upgrade && brew autoremove && brew cleanup`. More often
just churns versions for nothing.
