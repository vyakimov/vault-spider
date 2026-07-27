---
id: 01JEV000000000000000000145
title: Atlas Access Review 2024
type: review
created: 2024-01-19T09:00:00Z
updated: 2024-04-24T12:00:00Z
tags: [atlas, operations]
---
# Atlas Access Review 2024

## Meeting Summary

The January 2024 access-credential review convened on January 19th to audit service account permissions across Cedar, Harbor, and the dashboard. Seven accounts were evaluated for principle of least privilege compliance. Three findings were documented: one high-priority overpermissioned read-write role on the Harbor API (resolved by splitting into import-only and query roles), two medium-priority candidates for consolidation among PostgreSQL maintenance accounts. The session identified that field-deployed Cedar instances had differing SSH key management practices across sites, warranting standardization.

## Decisions and Follow-ups

Participants agreed that all new service accounts must submit to approval workflow via ticket before provisioning. Rotation intervals were set at 90 days for API credentials and 180 days for database accounts. A secondary review was scheduled for April to confirm the Harbor role split had been deployed and to address the Cedar key standardization. [[Atlas Third-Party Audit 2025]] was referenced as precedent for audit scope and thoroughness.

## Related Notes

- [[Atlas Access Review]] (current policy)
- [[Atlas Third-Party Audit 2025]] (external audit findings)
