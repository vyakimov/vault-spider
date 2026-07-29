---
updated: 2026-03-16T11:45:00
id: 01M6D00000000000000000000A
created: 2026-02-16T10:45:00
---
# papertrail Folder Structure

How OCR'd documents get filed by year and category after processing.

## Schema
Documents are stored in `/archive/<year>/<category>/`, where category is one of: taxes, medical, receipts, legal, utilities, other. The OCR pipeline extracts a date from the document and uses that to determine the year. Within each folder, files are named `<YYYYMMDD>_<description>.pdf`.

## Automation
When I scan a paper document, the Papertrail agent runs Tesseract OCR, then uses keyword matching to guess the category. Medical documents with "Dr." or "diagnosis" get filed to medical; utility bills with account numbers go to utilities. I review the categorization before archival, and manually fix misclassifications.
