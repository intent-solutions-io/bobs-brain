# Agent Engine Promotion Playbook

**Date:** 2025-12-11
**Status:** Active
**Type:** Runbook (Operator Guide)

## Overview

This playbook describes the process for promoting Agent Engine deployments from dev -> stage -> prod.

## Promotion Flow

```
DEV (Development)
  |
  | [Validated via ARV gates]
  v
STAGE (Pre-Production)
  |
  | [Validated + Manual Approval]
  v
PROD (Production)
```

## Pre-Promotion Checklist

### Dev -> Stage

Before promoting from dev to stage:

- [ ] Unit tests passing (`make test`)
- [ ] A2A contract validation passing (`make check-a2a-contracts`)
- [ ] ARV department checks passing (`make arv-department`)
- [ ] Drift detection clean (`make check-all`)
- [ ] Dev smoke tests passing
- [ ] Engine IDs configured in `config/agent_engine_envs.yaml`

### Stage -> Prod

Before promoting from stage to prod:

- [ ] All dev -> stage checks passing
- [ ] Stage smoke tests passing
- [ ] Stage health check OK
- [ ] Manual approval obtained (#deployments channel)
- [ ] Engine IDs configured for prod

## Commands

### View Current Mapping

```bash
# Show all agent mappings
make promote-agent-config-show

# Or directly:
python scripts/promote_agent_engine_config.py --agent all
```

### View Promotion Path

```bash
# Dev to Stage
make promote-agent-config-dev-to-stage

# Stage to Prod
make promote-agent-config-stage-to-prod
```

### Validate Promotion Readiness

```bash
# Validate dev -> stage (exits 2 if TODOs remain)
make promote-agent-config-validate-dev-to-stage

# Validate stage -> prod
make promote-agent-config-validate-stage-to-prod
```

## Configuration Updates

### After Deploying to an Environment

1. Get the Engine ID from deployment output or Vertex AI Console
2. Update `config/agent_engine_envs.yaml`:
   ```yaml
   agents:
     bob:
       environments:
         dev:
           engine_id: "projects/123/locations/us-central1/agents/abc123"
           status: "deployed"
   ```
3. Commit the change:
   ```bash
   git add config/agent_engine_envs.yaml
   git commit -m "config: update bob dev engine ID after deployment"
   ```

### Finding Engine IDs

**From Deployment Output:**
```
Agent deployed successfully!
Engine ID: projects/bobs-brain-dev/locations/us-central1/agents/abc123def456
```

**From Vertex AI Console:**
1. Go to Vertex AI > Agent Engine
2. Find your agent
3. Copy the full resource name

## Monitoring After Promotion

### Dev Environment

- Check Cloud Run logs
- Verify agent responds to test queries
- Monitor for errors in first hour

### Stage Environment

- Full smoke test suite
- Load testing if applicable
- Integration tests with external services

### Prod Environment

- Gradual rollout if supported
- Active monitoring for first 24 hours
- Rollback plan ready

## Rollback Procedure

If issues are discovered after promotion:

1. **Immediate:** Route traffic back to previous version
2. **Investigate:** Check logs, identify root cause
3. **Fix:** Update code, test in dev
4. **Re-promote:** Follow standard promotion flow

## Related Documentation

- Phase 31 Plan: `000-docs/187-AA-PLAN-phase-31-agent-engine-promotion-strategy.md`
- Deploy Script: `scripts/deploy_inline_source.py`
- Config File: `config/agent_engine_envs.yaml`
- ARV Checks: `scripts/check_inline_deploy_ready.py`

---
**Last Updated:** 2025-12-11
