---
updated: 2026-03-04T11:19:00
id: 01M6S000000000000000000004
created: 2026-02-04T10:23:00
---
# Fernweh Currency Conversion

A small cached exchange-rate lookup for budget tracking while travelling.

## Feature
When I log a budget item during a trip (e.g., "Restaurant: 45 EUR"), Fernweh converts it to my home currency (USD) using cached exchange rates. The conversion uses mid-market rates pulled from OpenExchangeRates once per trip to avoid overfetching.

## Caching
I cache exchange rates for 7 days so they don't change mid-trip. After 7 days, the rate is refreshed. This keeps conversions consistent within a trip while staying reasonably current.
