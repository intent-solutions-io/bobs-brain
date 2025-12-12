# Bob's Brain Environment Matrix

**Date:** 2025-12-12
**Type:** Guide
**Status:** Active
**Phase:** 43 - Stage Environment Scaffolding

## Overview

This document defines the three deployment environments for Bob's Brain and how they relate to each other.

## Environment Matrix

| Aspect | Dev | Stage | Prod |
|--------|-----|-------|------|
| **Purpose** | Development & experimentation | Pre-production validation | Live production |
| **Project ID** | `bobs-brain-dev` | `bobs-brain-staging` | `bobs-brain` |
| **Stability** | Unstable | Stable | Highly stable |
| **Data** | Synthetic/test | Test (prod-like) | Real user data |
| **Access** | Developers | QA + Developers | All users |

## Configuration Files

| Environment | Terraform Vars | Workflow |
|-------------|----------------|----------|
| Dev | `infra/terraform/envs/dev.tfvars` | Manual only (Agent Engine) |
| Stage | `infra/terraform/envs/staging.tfvars` | `.github/workflows/terraform-stage.yml` |
| Prod | `infra/terraform/envs/prod.tfvars` | `.github/workflows/terraform-prod.yml` |

## Environment Roles

### Dev (Development)

**Purpose:** Experimentation and active development

- Fast iteration, frequent changes
- May be broken at times
- Used for testing new features before stage
- Agent Engine deployments via `agent-engine-inline-dev-deploy.yml`

**Who uses it:**
- Developers building new features
- CI/CD for automated testing
- Local development integration

**Resources:**
- Smaller compute (n1-standard-2)
- 2 max replicas
- 5 gateway instances max

### Stage (Staging)

**Purpose:** Pre-production validation

- Production-like configuration
- Stable (not for experimentation)
- Final validation before prod
- Terraform deployments via `terraform-stage.yml`

**Who uses it:**
- QA team for validation
- Developers for final testing
- Stakeholders for demos

**Resources:**
- Production-like compute (n1-standard-4)
- 3 max replicas
- 10 gateway instances max

### Prod (Production)

**Purpose:** Live production system

- Highly stable, carefully managed
- Real user traffic
- Changes require approvals
- Terraform deployments via `terraform-prod.yml`

**Who uses it:**
- End users (via Slack)
- Production monitoring
- Business operations

**Resources:**
- Production compute (n1-standard-4)
- Auto-scaling replicas
- Full gateway capacity

## Promotion Path

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMOTION PATH                           │
│                                                             │
│   Dev → Stage → Prod                                        │
│                                                             │
│   1. Develop & test in Dev                                  │
│   2. Merge to main, deploy to Stage                         │
│   3. Validate in Stage (QA, smoke tests)                    │
│   4. If OK, deploy to Prod (requires approval)              │
└─────────────────────────────────────────────────────────────┘
```

### Promotion Checklist

**Dev → Stage:**
- [ ] Feature complete
- [ ] Unit tests passing
- [ ] ARV checks passing
- [ ] Documentation updated
- [ ] PR approved and merged

**Stage → Prod:**
- [ ] Stage deployment successful
- [ ] Smoke tests passing in stage
- [ ] No blocking issues
- [ ] Stakeholder approval (if required)
- [ ] Terraform plan reviewed

## Workflow Triggers

### Agent Engine Deployments

| Environment | Workflow | Trigger |
|-------------|----------|---------|
| Dev | `agent-engine-inline-dev-deploy.yml` | `workflow_dispatch` |
| Stage | `agent-engine-stage-deploy.yml` | `workflow_dispatch` |
| Prod | (via Terraform) | Terraform apply |

### Terraform Infrastructure

| Environment | Workflow | Plan Trigger | Apply Trigger |
|-------------|----------|--------------|---------------|
| Stage | `terraform-stage.yml` | PR to main | `workflow_dispatch` (apply=true) |
| Prod | `terraform-prod.yml` | PR to main | `workflow_dispatch` (apply=true) |

## SPIFFE ID Pattern

Each environment has its own SPIFFE ID:

```
spiffe://intent.solutions/agent/bobs-brain/{env}/{region}/{version}
```

Examples:
- Dev: `spiffe://intent.solutions/agent/bobs-brain/dev/us-central1/0.14.0`
- Stage: `spiffe://intent.solutions/agent/bobs-brain/staging/us-central1/0.14.0`
- Prod: `spiffe://intent.solutions/agent/bobs-brain/prod/us-central1/0.14.0`

## Secret Management

Each environment uses separate secrets:

| Secret | Dev | Stage | Prod |
|--------|-----|-------|------|
| Slack Bot Token | `xoxb-dev-*` | `xoxb-staging-*` | `xoxb-prod-*` |
| Slack Signing Secret | Dev secret | Staging secret | Prod secret |
| GCP Service Account | Dev SA | Staging SA | Prod SA |

Secrets are stored in:
- GitHub Secrets (for CI/CD)
- GCP Secret Manager (for runtime)

## Common Operations

### Deploy to Stage

```bash
# Via GitHub Actions (recommended)
# Go to Actions → Terraform Staging Deployment → Run workflow

# Or via CLI (for reference only)
gh workflow run terraform-stage.yml \
  --ref main \
  -f apply=false  # Plan only
```

### Promote to Prod

```bash
# 1. Ensure stage is working
# 2. Via GitHub Actions
gh workflow run terraform-prod.yml \
  --ref main \
  -f apply=false  # Plan first

# 3. Review plan, then apply
gh workflow run terraform-prod.yml \
  --ref main \
  -f apply=true
```

## Troubleshooting

### "Stage deployment failed"

1. Check terraform plan output
2. Verify staging.tfvars is valid
3. Check GCP project permissions
4. Review workflow logs

### "Stage behaves differently than dev"

1. Compare tfvars files for differences
2. Check resource sizes (stage is larger)
3. Verify secrets are configured for stage
4. Check SPIFFE IDs match environment

## References

- Phase 43 Plan: `000-docs/213-AA-PLAN-phase-43-stage-env-scaffolding.md`
- Terraform Prod Workflow: `.github/workflows/terraform-prod.yml`
- Terraform Stage Workflow: `.github/workflows/terraform-stage.yml`
- Hard Mode Rules: `000-docs/6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`

---
**Last Updated:** 2025-12-12
