# Phase 43: Stage Environment Scaffolding – PLAN

**Date:** 2025-12-12
**Status:** In Progress
**Branch:** `feature/phase-43-stage-env-scaffolding`

## Goals

Add stage environment config and CI workflow for Terraform. Config scaffolding only - no actual Terraform apply in this phase.

### What This Phase Achieves

1. **Stage Terraform workflow** – Dedicated workflow for stage environment
2. **Environment matrix doc** – Clear documentation of dev/stage/prod roles
3. **Validate existing stage.tfvars** – Ensure it works with current modules
4. **CI wiring** – workflow_dispatch for stage plan/apply

## Analysis of Existing Infrastructure

### Already Exists ✅

| Component | Location | Status |
|-----------|----------|--------|
| Dev tfvars | `infra/terraform/envs/dev.tfvars` | ✅ Complete |
| Staging tfvars | `infra/terraform/envs/staging.tfvars` | ✅ Exists |
| Prod tfvars | `infra/terraform/envs/prod.tfvars` | ✅ Complete |
| Prod workflow | `.github/workflows/terraform-prod.yml` | ✅ Working |

### What This Phase Adds

1. **Stage workflow** – `.github/workflows/terraform-stage.yml`
2. **Environment matrix doc** – `000-docs/214-GD-ENV-bobs-brain-env-matrix-dev-stage-prod.md`
3. **Update staging.tfvars** – Align version and config with dev/prod

## High-Level Steps

### Step 1: Update staging.tfvars

Align with dev.tfvars structure:
- Update `app_version` to current
- Add Bob/Foreman docker image vars
- Add knowledge hub config if missing

### Step 2: Create Stage Terraform Workflow

Create `.github/workflows/terraform-stage.yml`:
- Copy from terraform-prod.yml
- Modify for staging environment
- Add staging environment protection
- Support plan-only by default

### Step 3: Create Environment Matrix Doc

Document in `000-docs/214-GD-ENV-bobs-brain-env-matrix-dev-stage-prod.md`:
- Purpose of each environment
- Which workflows/tfvars for each
- Promotion path (dev → stage → prod)

### Step 4: Validate Terraform

Run `terraform validate` against staging.tfvars to confirm it works.

## Design Decisions

### Separate Workflow for Stage

Rather than modifying terraform-prod.yml to support multiple envs:
- Clearer separation of concerns
- Different approval requirements
- Easier to modify independently
- Matches "one workflow per environment" pattern

### Stage as Pre-Prod Validation

Stage environment purpose:
- Validate changes before production
- Test with production-like config
- Smoke test infrastructure changes
- Not for development experimentation

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `infra/terraform/envs/staging.tfvars` | Modify | Align with current structure |
| `.github/workflows/terraform-stage.yml` | Create | Stage Terraform workflow |
| `000-docs/213-AA-PLAN-*.md` | Create | This file |
| `000-docs/214-GD-ENV-*.md` | Create | Environment matrix doc |
| `000-docs/215-AA-REPT-*.md` | Create | AAR after completion |

---
**Last Updated:** 2025-12-12
