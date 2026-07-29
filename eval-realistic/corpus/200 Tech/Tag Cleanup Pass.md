---
updated: 2026-01-01T11:04:00
id: 01M6V000000000000000000065
created: 2026-07-01T10:08:00
---
# Tag Cleanup Pass

A periodic maintenance pass that merges near-duplicate tags across the vault to keep the tagging system useful.

## The Problem
Over months of note-taking, related concepts accumulated multiple tag variations: `network` and `networking`, `storage` and `backup` when they overlapped, `hardware-observation` and `hardware-note`. This fragmentation meant the same concept appeared in multiple tag facets, making systematic review harder. Tag searches would miss relevant notes just because of slight naming differences.

## Cleanup Process
I ran a full vault search on the most common tags and reviewed which could be consolidated. I merged `network*` variants into `network`, combined `storage` and `backup` where they overlapped into a combined tag, and simplified vague tags like `pending` that had lost meaning. Each merge required updating every affected note. The cleanup took about 3 hours but the resulting tag system is cleaner. Now a tag represents one clear concept and when I search by tag, I get the full set of related notes. I plan to do this quarterly as the vault grows.
