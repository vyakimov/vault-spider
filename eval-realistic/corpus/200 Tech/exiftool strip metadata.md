---
updated: 2026-03-18T15:15:00
id: 01M6E00000000000000000000T
created: 2026-02-16T12:15:00
---
`exiftool -all= image.jpg` removes all metadata; creates a backup with `_original` suffix. For batch: `exiftool -all= -overwrite_original *.jpg`. Read EXIF with `exiftool -GPS* -createdate -model image.jpg`. Extract specific fields: `exiftool -p '$filename: $DateTimeOriginal' *.jpg > dates.txt`.
