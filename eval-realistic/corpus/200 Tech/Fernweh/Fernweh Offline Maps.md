---
updated: 2026-02-03T11:08:00
id: 01M6S000000000000000000003
created: 2026-01-03T10:16:00
---
# Fernweh Offline Maps

Bundling offline map tiles for a trip before departure.

## Workflow
Before a trip, I use Fernweh's map interface to select a bounding box around the destination, then generate offline tiles. The tool downloads vector tiles from OpenStreetMap and bundles them as a SQLite database (~50-200 MB depending on area size and zoom levels).

## On Trip
Fernweh's mobile web app can serve maps offline using the local tile database. This works great for city exploration where I don't have cellular data. I usually bundle zoom levels 12-18 (enough for street-level navigation).
