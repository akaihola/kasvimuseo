---
name: privileged-account-vault-gate
description: Issue 075 requires a pre-rotation audit before production admin passwords change
metadata:
  node_type: memory
  type: project
---

`ansible/secure-production.yaml` runs the read-only privileged-account audit
before password rotation and stops when an active privileged account is outside
`kasvimuseo_admin_passwords`. Issue 075 records the account decision and the
production-owner action for the inactive `anja` account.
