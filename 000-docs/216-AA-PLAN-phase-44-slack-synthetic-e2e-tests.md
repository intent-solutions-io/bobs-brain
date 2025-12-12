# Phase 44: Slack Dev/Stage Synthetic E2E Tests – PLAN

**Date:** 2025-12-12
**Status:** In Progress
**Branch:** `feature/phase-44-slack-synthetic-e2e-tests`

## Goals

Build a synthetic Slack test harness that validates the Slack gateway without requiring real Slack.

### What This Phase Achieves

1. **Synthetic test harness** – HTTP-based tests simulating Slack events
2. **CI integration** – Run tests as part of CI pipeline (non-blocking initially)
3. **Dev and stage support** – Tests work against both environments
4. **No real Slack required** – Pure HTTP validation

## Design

### Test Strategy

The tests simulate Slack Events API payloads:
1. Construct valid Slack `app_mention` or `message.im` event JSON
2. POST to `/slack/events` endpoint
3. Validate:
   - 200 OK response
   - Correct JSON structure
   - No 4xx/5xx errors

### Why Synthetic?

- Real Slack requires credentials and workspace access
- Synthetic tests can run in CI without secrets
- Tests the gateway logic, not Slack integration
- Fast feedback in development

## High-Level Steps

### Step 1: Create Test Harness

Create `tests/slack_e2e/`:
- `__init__.py`
- `test_slack_gateway_synthetic_dev.py` - Dev environment tests
- `conftest.py` - Shared fixtures

### Step 2: Implement Tests

Tests to implement:
- Health check endpoint (`/health`)
- URL verification challenge
- App mention event (synthetic)
- Error handling (malformed payload)

### Step 3: Add Make Targets

```makefile
slack-synthetic-e2e-dev: ## Run Slack synthetic E2E tests against dev
    pytest tests/slack_e2e/test_slack_gateway_synthetic_dev.py

slack-synthetic-e2e-stage: ## Run Slack synthetic E2E tests against stage
    SLACK_GATEWAY_URL=$SLACK_GATEWAY_URL_STAGE pytest tests/slack_e2e/
```

### Step 4: Wire to CI

Add job to CI workflow (guarded by env var availability).

## Test Cases

| Test | Description | Expected |
|------|-------------|----------|
| `test_health_endpoint` | GET /health | 200 OK with status |
| `test_url_verification` | URL challenge | Returns challenge |
| `test_app_mention_synthetic` | Simulated mention | 200 OK |
| `test_invalid_payload` | Bad JSON | 200 OK (Slack expects 200) |

## Files to Create

| File | Purpose |
|------|---------|
| `tests/slack_e2e/__init__.py` | Package marker |
| `tests/slack_e2e/conftest.py` | Pytest fixtures |
| `tests/slack_e2e/test_slack_gateway_synthetic_dev.py` | Test implementation |
| `000-docs/216-AA-PLAN-*.md` | This file |
| `000-docs/217-AA-REPT-*.md` | AAR after completion |

## Limitations

- Tests don't verify actual Slack message delivery
- Tests don't verify Agent Engine response content
- Signature verification skipped in synthetic tests (no real secret)

---
**Last Updated:** 2025-12-12
