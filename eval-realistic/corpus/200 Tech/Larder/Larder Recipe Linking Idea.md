---
updated: 2026-02-15T11:34:00
id: 01M6C000000000000000000009
created: 2026-01-15T10:38:00
---
# Larder Recipe Linking Idea

A half-built idea to link pantry items to recipes that use them, so I can see "chicken breast" → [3 recipes] and quickly pick something for dinner.

## Prototype
I started building a simple recipe schema (ingredients list + quantities) and wrote a fuzzy matcher to link pantry items (e.g., "chicken breast, skin-on") to recipe ingredients (e.g., "chicken breast"). The prototype works but the ingredient name normalization is messy.

## Blockers
Recipes from different sources use wildly different naming conventions. Scaling the fuzzy matcher to handle all variations felt like a yak-shave. I shelved this to focus on core pantry features. Maybe revisit if I ever build a public recipe database.
