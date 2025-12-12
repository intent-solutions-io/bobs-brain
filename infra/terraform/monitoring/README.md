# Bob's Brain Monitoring Definitions

This directory contains observability definitions for Bob's Brain agent department.

## Contents

| File | Description |
|------|-------------|
| `dashboards_bobs_brain.json` | Dashboard panel definitions for Cloud Monitoring |
| `alerts_bobs_brain.yaml` | Alert policy definitions for Cloud Monitoring |
| `README.md` | This file |

## Usage

These files are **reference definitions**, not directly deployable Terraform resources.
They document what metrics we care about and what alerts should exist.

### Creating Actual Dashboards

1. **Manual Import**: Use Cloud Console to create dashboard, copy-paste panel configs
2. **Terraform**: Translate JSON to `google_monitoring_dashboard` resource
3. **API**: Use Cloud Monitoring API to create programmatically

### Creating Actual Alerts

1. **Terraform**: Translate YAML to `google_monitoring_alert_policy` resources
2. **Console**: Create manually using the definitions as reference
3. **API**: Use Monitoring API with the spec

## Key Metrics

### Agent Engine (Vertex AI)
- `aiplatform.googleapis.com/reasoning_engine/prediction/count` - Request count
- `aiplatform.googleapis.com/reasoning_engine/prediction/error_count` - Errors
- `aiplatform.googleapis.com/reasoning_engine/prediction/latency` - Response time
- `aiplatform.googleapis.com/reasoning_engine/prediction/token_count` - Token usage

### Cloud Run (Gateways)
- `run.googleapis.com/request_count` - Request count by status
- `run.googleapis.com/request_latencies` - Latency distribution
- `run.googleapis.com/container/instance_count` - Active instances

### Custom Metrics (Future)
- `custom.googleapis.com/bobs_brain/tool_call_count` - Tool usage
- `custom.googleapis.com/bobs_brain/a2a_call_duration_seconds` - A2A latency

## Environment Customization

Replace project IDs in filters:
- dev: `resource.labels.project_id="bobs-brain-dev"`
- stage: `resource.labels.project_id="bobs-brain-stage"`
- prod: `resource.labels.project_id="bobs-brain-prod"`

## See Also

- `000-docs/201-RB-OBSERVABILITY-bobs-brain-dashboard-and-alert-playbook.md`
- Cloud Monitoring documentation
- Vertex AI metrics documentation
