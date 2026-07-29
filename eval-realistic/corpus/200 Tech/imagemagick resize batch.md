---
updated: 2026-02-17T14:58:00
id: 01M6E00000000000000000000S
created: 2026-01-15T11:02:00
---
`mogrify -resize 1920x1080 -quality 85 *.jpg` resizes in-place (backup first!). Use `convert` for output: `convert -resize 50% input.jpg output.jpg`. Batch via `for f in *.jpg; do convert "$f" -resize 1280x "${f%.*}_thumb.jpg"; done`. Add `+append` to stitch images side-by-side; `-gravity center` positions layers.
