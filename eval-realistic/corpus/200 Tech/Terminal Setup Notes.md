---
updated: 2026-02-24T11:59:00
id: 01M6V00000000000000000000A
created: 2026-01-24T10:43:00
---
# Terminal Setup Notes

Shell, prompt, and font choices settled on after a lot of tinkering.

## What Stuck
I use bash (not zsh, not fish) because it's everywhere and I like the consistency. The prompt is simple: path + git branch (if in a repo) + exit code of last command (displayed as a color). This gives me instant feedback about whether the last thing worked. I switched to Inconsolata font years ago and never looked back—it's monospaced, readable at size 11, and doesn't have the quirky character spacing of Courier New.

## The Workflow
Terminal lives in a tiling window manager, usually half-screen. I have aliases for common git commands, a function to jump to frequently-accessed directories, and a simple history search bound to Ctrl+R. No fancy theming, no complex color schemes—the defaults are fine. The real win was settling on this setup and stopping the constant tinkering. I'm more productive working in a slightly-imperfect environment that I know cold than chasing the perfect setup.
