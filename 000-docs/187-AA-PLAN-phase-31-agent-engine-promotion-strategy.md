# Phase 31: Agent Engine Promotion Strategy

**Date:** 2025-12-11
**Status:** In Progress
**Branch:** `feature/phase-31-agent-engine-promotion-strategy`

## Objective

Define a promotion pattern for ReasoningEngines (dev -> stage -> prod) using config and documentation only. No actual deployments or API calls.

## Desired Flow

```
Dev Agent Engine (validated)
    |
    v  [Promotion Script - config only]
Stage Agent Engine (validated)
    |
    v  [Promotion Script - config only]
Prod Agent Engine (deployed via Terraform/CI)
```

## Non-Goals

- Modify or delete any existing Agent Engine instances
- Add gcloud commands
- Actually perform promotions in GCP
- Change runtime architecture

## Deliverables

1. **Agent Engine Environment Mapping**
   - `config/agent_engine_envs.yaml` - Maps agents to engine IDs per environment
   - Clear TODO placeholders for unknown IDs

2. **Promotion Helper Script**
   - `scripts/promote_agent_engine_config.py`
   - Reads config, shows mapping/diff
   - No API calls - config validation only

3. **Make Targets**
   - `promote-agent-config-dev-to-stage`
   - `promote-agent-config-stage-to-prod`

4. **Operator Documentation**
   - Agent Engine promotion playbook
   - CLAUDE.md updates

## Implementation Steps

1. Create `config/agent_engine_envs.yaml` with mapping structure
2. Create promotion helper script (config-only, no API)
3. Add Make targets for promotion workflow
4. Update CLAUDE.md with promotion section
5. Create promotion playbook runbook

---
**Last Updated:** 2025-12-11
