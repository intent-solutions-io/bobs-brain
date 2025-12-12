# Phase 36: Stage Agent Engine CI Deploy Workflow - AAR

**Date:** 2025-12-12
**Status:** Complete
**Branch:** `feature/phase-36-stage-agent-engine-ci-deploy`

## Summary

Created CI-only workflow to deploy Bob and Foreman to stage Vertex AI Agent Engine. The workflow enforces ARV gates and uses the existing inline deployment pattern without any direct gcloud commands.

## What Was Built

### 1. Updated Deploy Script

**File:** `scripts/deploy_inline_source.py`

Changes:
- Added `stage` as valid environment alias (maps to `staging`)
- Updated argparse choices to include `stage`
- Script normalizes `stage` → `staging` internally

### 2. Make Targets

**File:** `Makefile`

New targets:
- `deploy-bob-stage` - Deploy Bob to stage Agent Engine
- `deploy-foreman-stage` - Deploy Foreman to stage Agent Engine
- `deploy-stage-all` - Deploy both agents sequentially
- `deploy-stage-dry-run` - Validate stage deployment config (dry-run)

Environment variables used:
- `PROJECT_ID_STAGE` / `GCP_PROJECT_ID_STAGE` - Stage GCP project
- `LOCATION_STAGE` / `GCP_LOCATION` - Stage region (default: us-central1)

### 3. GitHub Actions Workflow

**File:** `.github/workflows/agent-engine-stage-deploy.yml`

Features:
- `workflow_dispatch` only (manual trigger required)
- Input: agent selection (`bob`, `foreman`, `both`)
- ARV checks run before deployment
- Dry-run validation before actual deployment
- Clear error message if stage configuration missing
- Uses existing WIF authentication pattern

Steps:
1. Validate stage configuration
2. Checkout repository
3. Setup Python 3.12
4. Install dependencies
5. Authenticate via WIF
6. Run ARV checks
7. Dry-run validation
8. Deploy selected agent(s)
9. Report status

## Files Changed

| File | Action |
|------|--------|
| `scripts/deploy_inline_source.py` | Modified - added stage env support |
| `Makefile` | Modified - added stage deploy targets |
| `.github/workflows/agent-engine-stage-deploy.yml` | Created |
| `000-docs/203-AA-PLAN-phase-36-stage-agent-engine-ci-deploy-workflow.md` | Created |
| `000-docs/204-AA-REPT-phase-36-stage-agent-engine-ci-deploy-workflow.md` | Created |

## Design Decisions

### Why `stage` as alias?

The deploy script originally used `staging`, but our convention uses `stage` (matching `dev`, `prod`). Added `stage` as an alias that normalizes to `staging` internally for consistency.

### Why separate Make targets?

Following the existing pattern from dev deployment, keeping targets separate allows:
- Deploy individual agents independently
- Chain deployments with `deploy-stage-all`
- Validate configuration with `deploy-stage-dry-run`

### Why no direct gcloud commands?

Per Hard Mode Rule R4, all deployments must go through CI. The Python script handles all GCP API calls, avoiding direct shell commands that could bypass CI controls.

## Configuration Required

To use this workflow, configure in GitHub repository settings:

### Environment Variables (vars)
- `PROJECT_ID_STAGE` - GCP project ID for stage
- `LOCATION_STAGE` - GCP region (default: us-central1)

### Secrets
- `GCP_WORKLOAD_IDENTITY_PROVIDER` - WIF provider (existing)
- `GCP_SERVICE_ACCOUNT` - Service account (existing)

## Usage

### Via GitHub Actions (Recommended)
1. Go to Actions → "Agent Engine Deploy - Stage (Manual)"
2. Click "Run workflow"
3. Select agent(s) to deploy
4. Monitor workflow for success/failure

### Via Make (Local testing only)
```bash
# Dry-run validation
make deploy-stage-dry-run

# Deploy with credentials (CI environment)
export PROJECT_ID_STAGE=my-stage-project
export LOCATION_STAGE=us-central1
make deploy-bob-stage
make deploy-foreman-stage
# or
make deploy-stage-all
```

## Limitations

- **Code Ready, Infra May Be Incomplete**: The workflow is functional but requires stage GCP project configuration
- **No Terraform Changes**: This phase only adds Agent Engine deployment, not infrastructure
- **Manual Trigger Only**: Intentionally requires manual workflow_dispatch for stage

## Next Steps

1. Configure `PROJECT_ID_STAGE` in GitHub environment variables
2. Test workflow with actual stage project
3. Consider adding post-deployment smoke tests

---
**Last Updated:** 2025-12-12
