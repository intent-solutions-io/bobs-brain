# IAM Department Template

**Generated from:** bobs-brain
**Template Version:** 1.0.0
**Date Generated:** {{DATE}}

## Overview

This is a starter template for building ADK-based IAM (Intent Agent Model) departments. It follows the patterns established in `bobs-brain` and provides a minimal skeleton for:

- Foreman agent (orchestrator)
- Specialist agents (workers)
- Terraform infrastructure
- GitHub Actions CI/CD
- Documentation structure

## Quick Start

1. **Replace placeholders:**
   - `{{PROJECT_ID}}` → Your GCP project ID
   - `{{SPIFFE_ID}}` → Your agent SPIFFE ID
   - `{{ORG_NAME}}` → Your organization name
   - `{{DATE}}` → Current date

2. **Update agent names:**
   - Rename `foreman/` to your orchestrator name
   - Add specialists in `specialists/`

3. **Configure infrastructure:**
   - Update `infra/terraform/` variables
   - Set up WIF (Workload Identity Federation)

4. **Initialize git:**
   ```bash
   git init
   git add .
   git commit -m "chore: initialize from IAM department template"
   ```

## Directory Structure

```
.
├── 000-docs/          # Documentation (R6 compliant)
├── agents/            # ADK agents
│   ├── foreman/       # Orchestrator agent
│   └── specialists/   # Worker agents
├── infra/             # Infrastructure as Code
│   └── terraform/     # Terraform modules
├── service/           # Cloud Run gateways (R3)
├── scripts/           # Utility scripts
├── tests/             # Test suites
└── .github/           # CI/CD workflows
    └── workflows/
```

## Hard Mode Rules

This template follows ADK Hard Mode rules:

- **R1:** ADK-Only (no LangChain, CrewAI, custom frameworks)
- **R2:** Vertex AI Agent Engine runtime
- **R3:** Gateway separation (Cloud Run proxies only)
- **R4:** CI-only deployments (no manual gcloud)
- **R5:** Dual memory wiring (Session + MemoryBank)
- **R6:** Single doc folder (`000-docs/` with NNN-CC-ABCD naming)
- **R7:** SPIFFE ID propagation
- **R8:** Drift detection

## Reference Implementation

See `bobs-brain` repository for full implementation:
- https://github.com/intent-solutions-io/bobs-brain

---
**Template Source:** bobs-brain v0.14.x
