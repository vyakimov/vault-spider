---
updated: 2026-07-13T11:12:00
id: 01M6A00000000000000000000H
created: 2026-06-13T10:24:00
---
# Marionette Onboarding a New Tool

The checklist for adding a new allowlisted tool to the Marionette gateway.

## Steps
1. Define the tool schema in YAML (inputs, outputs, error cases). 2. Add integration tests that mock the tool and verify the gateway parses responses correctly. 3. Write a playbook example showing the tool in use. 4. Test the playbook manually over Signal. 5. Document the tool's rate limits and failure modes in a runbook. 6. Add the tool to the allowlist and restart the gateway.

## Vetting
Before adding, I check: Does the tool need credentials (if so, how are they stored)? Can it delete data (if so, require confirmation)? Is it rate-limited (if so, add jitter to avoid hammering)? Most tools take 30 minutes to onboard once I've written the schema.
