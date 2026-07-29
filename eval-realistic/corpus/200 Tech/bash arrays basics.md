---
updated: 2026-06-09T13:21:00
id: 01M6E000000000000000000277
created: 2026-06-08T18:09:00
---
`arr=(one two three)` declares array. `${arr[0]}` is first element, `${arr[@]}` all elements. `${#arr[@]}` is length. Use `for x in "${arr[@]}"` to iterate safely with spaces.
