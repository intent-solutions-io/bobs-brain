# Bob's Brain Reference Map

**Date:** 2025-12-11
**Purpose:** Master index for navigating bobs-brain as a reference/template repository

## Quick Navigation

| Need To... | Go To |
|------------|-------|
| Understand the architecture | [Architecture Section](#architecture) |
| Deploy agents | [Deployment Section](#deployment) |
| Add new agents | [Agent Development Section](#agent-development) |
| Check compliance | [Standards Section](#standards-6767-series) |
| Onboard new engineer | [New Engineer Quickstart](192-OVERVIEW-new-engineer-quickstart.md) |

---

## Phases & AARs

Recent phases (reverse chronological):

| Phase | Doc ID | Description |
|-------|--------|-------------|
| 32 | 190-192 | Reference Template Hardening |
| 31 | 187-189 | Agent Engine Promotion Strategy |
| 30 | 185-186 | Stage Environment Baseline |
| 27 | 183-184 | Deployment Validation |
| 26 | 181-182 | Repository Cleanup & Release |
| 25 | (PR focused) | Slack Bob Hardening |
| 24 | 164-165 | Slack Bob CI Deploy & Restore |
| 23 | 155-157 | Inline Deploy Implementation |
| 21-22 | 150-154 | Agent Engine Dev Wiring |

Full phase history: See doc range 050-184 for all phase AARs.

---

## Standards (6767 Series)

**Master Catalog:** `6767-DR-INDEX-bobs-brain-standards-catalog.md`

### Core Standards

| Doc | Title | Purpose |
|-----|-------|---------|
| `6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md` | Hard Mode Rules (R1-R8) | Architectural constraints |
| `6767-LAZY-DR-STND-adk-lazy-loading-app-pattern.md` | Lazy Loading Pattern | Agent initialization |
| `6767-INLINE-DR-STND-inline-source-deployment-for-vertex-agent-engine.md` | Inline Deployment | Deploy without serialization |
| `6767-DR-STND-agentcards-and-a2a-contracts.md` | AgentCards & A2A | Inter-agent communication |
| `6767-DR-STND-document-filing-system-standard-v3.md` | Doc Filing System | How to name docs |

### Deployment Standards

| Doc | Title | Purpose |
|-----|-------|---------|
| `6767-DR-INDEX-agent-engine-a2a-inline-deploy.md` | Deployment Sub-Index | All deployment docs |
| `6767-DR-STND-slack-gateway-deploy-pattern.md` | Slack Gateway | Cloud Run proxy pattern |
| `6767-DR-STND-arv-minimum-gate.md` | ARV Gates | Deployment readiness checks |

---

## Runbooks

| Doc | Title | Use Case |
|-----|-------|----------|
| `6767-RB-OPS-adk-department-operations-runbook.md` | Operations Runbook | Day-to-day ops |
| `188-RB-OPER-agent-engine-promotion-playbook.md` | Promotion Playbook | Dev -> Stage -> Prod |
| `6767-SLKDEV-DR-GUIDE-slack-dev-integration-operator-guide.md` | Slack Integration | Slack setup |
| `070-OD-RBOK-deployment-runbook.md` | General Deployment | Legacy deployment guide |

---

## Architecture

| Doc | Title | Purpose |
|-----|-------|---------|
| `082-AT-ARCH-department-complete-structure.md` | Department Structure | Full org chart |
| `094-AT-ARCH-iam-swe-pipeline-orchestration.md` | SWE Pipeline | Workflow orchestration |
| `101-AT-ARCH-agent-engine-topology-and-envs.md` | Engine Topology | Environment layout |
| `102-AT-ARCH-cloud-run-gateways-and-agent-engine-routing.md` | Gateway Routing | A2A routing |

---

## Infrastructure

### Terraform

| Path | Purpose |
|------|---------|
| `infra/terraform/envs/dev.tfvars` | Dev environment config |
| `infra/terraform/envs/stage.tfvars` | Stage environment config |
| `infra/terraform/envs/prod.tfvars` | Production config |
| `infra/terraform/modules/` | Reusable TF modules |

### CI Workflows

| Workflow | Purpose |
|----------|---------|
| `.github/workflows/ci.yml` | Main CI (lint, test, checks) |
| `.github/workflows/terraform-prod.yml` | Production Terraform (R4) |
| `.github/workflows/terraform-stage.yml` | Stage Terraform (plan-only) |
| `.github/workflows/a2a-compliance.yml` | A2A contract validation |

---

## Agent Development

### Key Files Per Agent

```
agents/<agent-name>/
  ├── agent.py           # Agent definition (LlmAgent)
  ├── app.py             # Lazy-loading App pattern
  ├── a2a_card.py        # AgentCard definition
  ├── tools/             # Agent-specific tools
  └── .well-known/
      └── agent-card.json  # Published AgentCard
```

### Shared Components

| Path | Purpose |
|------|---------|
| `agents/shared_contracts.py` | Pydantic models for all agents |
| `agents/a2a/types.py` | A2A protocol types |
| `agents/config/` | Shared configuration |

---

## Config Files

| File | Purpose |
|------|---------|
| `config/agent_engine_envs.yaml` | Engine ID mapping per env |
| `config/repos.yaml` | Target repos for SWE pipeline |
| `VERSION` | Current version |
| `CLAUDE.md` | AI assistant guidance |

---

## Legacy / Reference Directories

These subdirectories exist for reference but are not part of active development:

| Directory | Purpose |
|-----------|---------|
| `000-docs/001-usermanual/` | ADK reference notebooks |
| `000-docs/google-reference/` | Symlink to local ADK docs |

**Note:** Per R6, all new docs should be flat files in `000-docs/`, not in subdirectories.

---

## See Also

- [New Engineer Quickstart](192-OVERVIEW-new-engineer-quickstart.md)
- [CLAUDE.md](../CLAUDE.md) - AI assistant guidance
- [README.md](../README.md) - Repository overview

---
**Last Updated:** 2025-12-11
