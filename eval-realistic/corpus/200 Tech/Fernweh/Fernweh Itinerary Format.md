---
updated: 2026-01-02T11:57:00
id: 01M6S000000000000000000002
created: 2026-07-02T10:09:00
---
# Fernweh Itinerary Format

The markdown-based itinerary format Fernweh parses into a timeline view.

## Syntax
Itineraries are written as markdown with timestamps: `## 2026-08-15 10:00 AM | Activity Name`. Fernweh parses the date, time, and activity name, then renders a timeline sorted by time. Activities can include multi-line descriptions and links to accommodations or restaurants.

## Example
```
## 2026-08-15 10:00 AM | Arrive at hotel
Check in starts at 3 PM, luggage storage available before then.

## 2026-08-15 06:00 PM | Dinner at Taverna
Reservation for 4 under [name]. Address: [address].
```

The timeline view shows these activities in order, with filters to collapse/expand by day or category.
