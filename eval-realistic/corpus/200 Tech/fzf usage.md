---
updated: 2026-01-04T17:39:00
id: 01M6E000000000000000000038
created: 2026-07-02T12:51:00
---
`fzf` opens fuzzy finder on stdin; `cat file.txt | fzf` to search lines. Integrate with shell: `CTRL-R` for history search (after `source <(fzf --bash)`), `CTRL-T` for file path completion. Use `--preview` to show file contents: `fzf --preview 'cat {}'`. Pipe results: `fzf --multi | xargs rm` to delete multiple files.
