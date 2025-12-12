# Phase 45: Resilience & Error-Handling Pass – PLAN

**Date:** 2025-12-12
**Status:** In Progress
**Branch:** `feature/phase-45-resilience-and-error-handling`

## Goals

Harden error handling in Slack gateway and A2A orchestration path.

### What This Phase Achieves

1. **Timeouts** – Configurable timeouts for Agent Engine calls
2. **Retries** – Bounded retries for transient failures
3. **Fallback messages** – User-friendly error responses
4. **Tests** – Cover main failure modes
5. **Documentation** – Operational error handling guide

## Analysis

### Current State

The Slack gateway (`service/slack_webhook/main.py`) already has:
- Basic try/except blocks
- Logging of errors
- User-friendly fallback messages

### What Needs Enhancement

| Area | Current | Target |
|------|---------|--------|
| Timeouts | Fixed 30s/60s | Configurable via env var |
| Retries | None | 1 retry for 5xx errors |
| Correlation ID | None | Add request/trace ID to logs |
| Error categorization | Generic | Structured error types |

## High-Level Steps

### Step 1: Enhance Gateway Error Handling

1. Add configurable timeout via `AGENT_ENGINE_TIMEOUT_SECONDS`
2. Add retry logic for transient failures (5xx only)
3. Add correlation ID to all log entries
4. Categorize errors (auth, timeout, 5xx, validation)

### Step 2: Add Gateway Tests

Create `tests/slack_gateway/`:
- `test_error_handling.py` – Test error scenarios
- Mock Agent Engine failures
- Verify fallback responses

### Step 3: Create Operational Runbook

Document in `000-docs/219-RB-OPS-bobs-brain-error-handling-and-resilience.md`:
- Error types and their handling
- Log locations and patterns
- Common causes and remediation

## Design Decisions

### Retry Policy

Single retry only:
- Retries are safe for GET-like queries
- Agent Engine calls are idempotent (query only)
- Max 1 retry to avoid compounding delays
- Only retry on 5xx (server errors)

### Timeout Configuration

Default 60s with env var override:
- Agent Engine calls can be slow (LLM processing)
- Too short = frequent timeouts
- Too long = poor user experience
- Allow operator tuning via env var

### Correlation ID

Use request ID pattern:
- Generate UUID per request
- Include in all log entries
- Pass to Agent Engine (if supported)
- Makes debugging multi-service flows easier

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `service/slack_webhook/main.py` | Modify | Add resilience logic |
| `tests/slack_gateway/__init__.py` | Create | Package marker |
| `tests/slack_gateway/test_error_handling.py` | Create | Error handling tests |
| `000-docs/218-AA-PLAN-*.md` | Create | This file |
| `000-docs/219-RB-OPS-*.md` | Create | Operational runbook |
| `000-docs/220-AA-REPT-*.md` | Create | AAR after completion |

## Limitations

- Retry logic only for Agent Engine calls, not Slack API
- Correlation ID not propagated to Agent Engine (API limitation)
- No circuit breaker (complexity vs value)

---
**Last Updated:** 2025-12-12
