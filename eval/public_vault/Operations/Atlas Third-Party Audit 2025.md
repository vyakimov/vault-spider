---
id: 01JEV000000000000000000158
title: Atlas Third-Party Audit 2025
type: review
created: 2025-05-06T09:00:00Z
updated: 2026-08-11T12:00:00Z
tags: [atlas, operations]
---
# Atlas Third-Party Audit 2025

## Audit Scope and Timeline

An external security audit was conducted by CyberAssure Inc. over 4 weeks in May-June 2025. The audit covered infrastructure security (Cedar and Harbor), network architecture, PostgreSQL database hardening, dashboard authentication, and business continuity procedures. Site visits were conducted at two field locations to assess physical security and operational practices.

## Key Findings

**Critical Findings (0)**: None. All critical systems met or exceeded security baselines.

**High Findings (2)**:
1. Dashboard API did not enforce rate limiting; attackers could enumerate users. Mitigation: rate limiter deployed in June, limiting to 100 requests per minute per IP.
2. Field site backup appliances lacked encryption at rest; if physically compromised, data could be extracted. Mitigation: full-disk encryption deployed to all backup appliances by August 2025.

**Medium Findings (4)**:
1. Harbor API lacked request signing; MITM attacks could replay batches. Mitigation: HMAC signing implemented and deployed.
2. PostgreSQL backlog of unpatched security updates. Mitigation: patch cycle schedule established, applying updates monthly.
3. Cedar firmware updates downloaded over unencrypted HTTP. Mitigation: TLS pinning and manifest signing deployed.
4. Field technician SSH keys not centrally managed. Mitigation: SSH key rotation procedure updated; manual key rotation scheduled.

**Low Findings (6)**: Documentation gaps, log retention misconfigurations, and access control documentation inconsistencies. These are being addressed through process improvements and documentation updates.

## Audit Recommendations

The auditors referenced [[Atlas Backup Policy Draft 2023]] as evidence that backup procedures had evolved significantly since 2023, and recommended that the current backup policy (adopted in late 2024) be documented formally and included in annual audit scope.

Recommendations also included: establish a formal change management process, implement configuration drift detection, conduct penetration testing annually, and establish a metrics dashboard for security KPIs.

## Remediation Progress

As of June 2026, all critical and high findings have been remediated. 3 of 4 medium findings are resolved; SSH key management remains in progress and is scheduled for completion by September 2026. All low findings are resolved through documentation updates.

## Follow-up Audit

A follow-up limited audit is scheduled for Q4 2026 to verify remediation effectiveness. Cost of the 2025 audit was $18,400.
