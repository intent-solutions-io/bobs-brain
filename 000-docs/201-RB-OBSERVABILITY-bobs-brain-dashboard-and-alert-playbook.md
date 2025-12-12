# Bob's Brain Observability Playbook

**Date:** 2025-12-11
**Type:** Runbook
**Audience:** DevOps, SRE, Platform Engineers

## Overview

This playbook documents the observability strategy for Bob's Brain agent department. Use it to:
- Understand which metrics matter and why
- Set up monitoring for new environments
- Adapt patterns for other agent repositories

## Key Metrics

### Why These Metrics?

| Metric | Why It Matters | What to Watch For |
|--------|---------------|-------------------|
| **Prediction Count** | Traffic volume, usage patterns | Sudden drops (outage), spikes (load) |
| **Error Count** | Service health | Rate > 5% indicates problem |
| **Latency P95** | User experience | > 30s frustrates users |
| **Token Usage** | Cost, complexity | Unexpected spikes increase bills |
| **5xx Errors** | Gateway health | Any 5xx is actionable |
| **Instance Count** | Capacity | Near max = scaling needed |

### Metric Sources

1. **Vertex AI Agent Engine** (primary)
   - Predictions, errors, latency, tokens
   - Source: `aiplatform.googleapis.com/reasoning_engine/*`

2. **Cloud Run Gateways** (secondary)
   - HTTP metrics for Slack and A2A gateways
   - Source: `run.googleapis.com/*`

3. **Custom Metrics** (future)
   - Tool call counts, A2A call duration
   - Source: `custom.googleapis.com/bobs_brain/*`

## Dashboards

### Dashboard Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Agent Engine Overview                                        │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Prediction      │ │ Error Count     │ │ Latency P95     │ │
│ │ Count           │ │                 │ │                 │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Gateway Health                                               │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Slack Requests  │ │ 5xx Errors      │ │ Gateway Latency │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Tool Calls & A2A                                             │
│ ┌───────────────────────────┐ ┌───────────────────────────┐ │
│ │ Tool Call Count (by tool) │ │ A2A Call Duration         │ │
│ └───────────────────────────┘ └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Creating Dashboards

1. Navigate to Cloud Monitoring → Dashboards
2. Create new dashboard
3. Add widgets using metrics from `infra/terraform/monitoring/dashboards_bobs_brain.json`
4. Apply environment filter (project_id)

## Alerts

### Alert Severity Matrix

| Environment | Error Rate | Latency | Zero Traffic | 5xx Gateway |
|-------------|-----------|---------|--------------|-------------|
| **dev**     | LOW       | LOW     | LOW          | MEDIUM      |
| **stage**   | MEDIUM    | MEDIUM  | MEDIUM       | HIGH        |
| **prod**    | CRITICAL  | HIGH    | HIGH         | CRITICAL    |

### Required Alerts (Minimum)

1. **Bob Agent High Error Rate** - Core agent failing
2. **Slack Gateway 5xx Burst** - User-facing failures
3. **Agent Engine Zero Traffic** - Dead agent detection
4. **Gateway High Latency** - Performance degradation

### Setting Up Alerts

1. Review `infra/terraform/monitoring/alerts_bobs_brain.yaml`
2. Create alert policies in Cloud Monitoring
3. Configure notification channels (PagerDuty, Slack, email)
4. Test alerts with synthetic failures

## Incident Response

### Error Rate Spike

```
1. Check Cloud Logging for error details
   gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" --limit=50

2. Review recent deployments
   git log --oneline -10

3. Check Vertex AI Agent Engine status
   Console → Vertex AI → Agent Builder → Reasoning Engines

4. If recent deploy: rollback
   gh workflow run terraform-prod.yml (with previous version)
```

### Zero Traffic Alert

```
1. Verify actual zero traffic (not false alarm)
   Check dashboard for traffic patterns

2. Test Slack bot manually
   @Bob hello

3. Check gateway health
   curl https://<gateway-url>/health

4. Check Agent Engine status
   Console → Vertex AI → Agent Builder

5. If gateway down: check Cloud Run logs
   gcloud run services logs read slack-webhook
```

### High Latency

```
1. Check token usage (complex queries use more tokens)
2. Check concurrent requests (scaling issue?)
3. Review Gemini API quotas
4. Check for infinite loops in agent logic
```

## Adapting for New Projects

When using bobs-brain as a template for a new agent repository:

### Step 1: Copy Monitoring Definitions

```bash
cp -r infra/terraform/monitoring/ <new-repo>/infra/terraform/monitoring/
```

### Step 2: Update Project References

In `dashboards_bobs_brain.json`:
- Replace `bobs-brain-*` with your project IDs

In `alerts_bobs_brain.yaml`:
- Replace `bob` filter strings with your agent names
- Update notification channels

### Step 3: Adjust Thresholds

Review and adjust based on your agent's characteristics:
- Expected latency (simpler agents may be faster)
- Error tolerance (critical agents need lower thresholds)
- Traffic patterns (business hours only? 24/7?)

### Step 4: Create Resources

Either:
1. Manual: Create via Cloud Console using definitions as reference
2. Terraform: Translate definitions to `google_monitoring_*` resources
3. API: Use Cloud Monitoring API programmatically

## Metrics Reference

### Agent Engine Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `reasoning_engine/prediction/count` | Total predictions | count |
| `reasoning_engine/prediction/error_count` | Failed predictions | count |
| `reasoning_engine/prediction/latency` | Response time | ms |
| `reasoning_engine/prediction/token_count` | Tokens used | count |

### Cloud Run Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `request_count` | Total requests | count |
| `request_latencies` | Response time | ms |
| `container/instance_count` | Active instances | count |
| `container/cpu/utilization` | CPU usage | % |
| `container/memory/utilization` | Memory usage | % |

## See Also

- `infra/terraform/monitoring/dashboards_bobs_brain.json`
- `infra/terraform/monitoring/alerts_bobs_brain.yaml`
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Vertex AI Metrics](https://cloud.google.com/vertex-ai/docs/predictions/monitor)

---
**Last Updated:** 2025-12-11
