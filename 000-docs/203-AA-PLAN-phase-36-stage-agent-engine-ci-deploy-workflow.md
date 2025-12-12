# Phase 36: Stage Agent Engine CI Deploy Workflow

**Date:** 2025-12-12
**Status:** In Progress
**Branch:** `feature/phase-36-stage-agent-engine-ci-deploy`

## Objective

Create a CI-only workflow to deploy Bob and Foreman to the **stage** Vertex AI Agent Engine environment. This workflow:

1. Uses the existing `scripts/deploy_inline_source.py` script
2. Is triggered manually via `workflow_dispatch`
3. Enforces ARV gates before deployment
4. Does NOT use direct `gcloud` commands - everything through Python scripts

## Inputs

- **Phase 23/24**: Existing dev inline deployment patterns
- **Phase 33/34**: Dev E2E simulation and stage Terraform dry-run
- **Existing Scripts**:
  - `scripts/deploy_inline_source.py` - Core deployment logic
  - `scripts/check_inline_deploy_ready.py` - ARV validation

## Non-Goals

- Production deployment (out of scope)
- Terraform apply (infrastructure changes)
- Slack gateway changes (handled separately)

## Design Decisions

### 1. Environment Naming

The deploy script accepts `--env` with values: `dev`, `staging`, `prod`. For consistency with our conventions, we'll:
- Accept `stage` as an alias for `staging` in the script
- Use environment variable `DEPLOYMENT_ENV=stage`

### 2. Make Targets

New Make targets following existing patterns:
- `deploy-bob-stage` - Deploy Bob to stage
- `deploy-foreman-stage` - Deploy Foreman to stage
- `deploy-stage-all` - Deploy both sequentially

### 3. GitHub Actions Workflow

New workflow: `.github/workflows/agent-engine-stage-deploy.yml`
- Trigger: `workflow_dispatch` only (manual)
- Inputs: agent selection (bob, foreman, both)
- Steps: Checkout → Setup → Auth → ARV checks → Deploy

### 4. WIF Authentication

Reuse the existing WIF (Workload Identity Federation) setup from `terraform-prod.yml`:
- `GCP_WORKLOAD_IDENTITY_PROVIDER` secret
- `GCP_SERVICE_ACCOUNT` secret

## Implementation Steps

1. [ ] Update `scripts/deploy_inline_source.py` to accept `stage` as env alias
2. [ ] Add Make targets for stage deployment
3. [ ] Create `.github/workflows/agent-engine-stage-deploy.yml`
4. [ ] Add environment variables for stage (PROJECT_ID_STAGE, LOCATION_STAGE)
5. [ ] Test workflow file is valid YAML

## Success Criteria

- [ ] `make deploy-bob-stage` works (with appropriate env vars)
- [ ] `make deploy-foreman-stage` works (with appropriate env vars)
- [ ] GitHub Actions workflow passes syntax validation
- [ ] ARV gates are enforced before any deployment

## Fallbacks

- If stage project configuration is missing: Script exits with clear error message
- If WIF credentials not set: Workflow fails with explicit hint to configure secrets

## Related Documents

- `000-docs/6767-INLINE-DR-STND-inline-source-deployment-for-vertex-agent-engine.md`
- `000-docs/152-AA-REPT-phase-21-agent-engine-dev-first-live-deploy-and-smoke-tests.md`
- `.github/workflows/agent-engine-inline-dev-deploy.yml` (reference pattern)

---
**Last Updated:** 2025-12-12
