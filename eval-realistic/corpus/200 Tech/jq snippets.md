---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000001
created: 2025-10-14T15:22:40
---
A [[technote]] and [[code snippet]] for jq. Part of [[code snippet|code snippets]].

Pull one field out of every element of an array:
`jq -r '.[].name' releases.json`

Group and count:
`jq 'group_by(.status) | map({status: .[0].status, n: length})'`

Raw strings without quotes need `-r`, forgetting it is 90% of my jq debugging.

#finalised
