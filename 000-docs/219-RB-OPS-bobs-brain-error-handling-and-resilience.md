# Bob's Brain Error Handling & Resilience Runbook

**Date:** 2025-12-12
**Version:** 0.8.0
**Phase:** 45 - Resilience & Error-Handling Pass

## Overview

This runbook documents error handling patterns, resilience configuration, and troubleshooting procedures for the Bob's Brain Slack gateway.

## Architecture

```
User (Slack) → Slack Webhook Gateway → A2A Gateway → Agent Engine
                     ↓
            [Error Handling]
            - Correlation ID tracking
            - Configurable timeouts
            - Retry logic (5xx only)
            - User-friendly messages
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ENGINE_TIMEOUT_SECONDS` | 60 | HTTP timeout for Agent Engine calls |
| `AGENT_ENGINE_RETRY_ENABLED` | true | Enable retry on 5xx errors |
| `AGENT_ENGINE_MAX_RETRIES` | 1 | Maximum retry attempts |

### Tuning Recommendations

**For high-latency environments:**
```bash
AGENT_ENGINE_TIMEOUT_SECONDS=120  # Increase to 2 minutes
```

**For fast-fail scenarios:**
```bash
AGENT_ENGINE_TIMEOUT_SECONDS=30
AGENT_ENGINE_RETRY_ENABLED=false
```

**For maximum resilience:**
```bash
AGENT_ENGINE_TIMEOUT_SECONDS=90
AGENT_ENGINE_RETRY_ENABLED=true
AGENT_ENGINE_MAX_RETRIES=2
```

## Error Types

### 1. HTTP Status Errors

**Error Type:** `http_status`

**5xx Errors (Server Errors) - Retryable:**
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

**4xx Errors (Client Errors) - Not Retried:**
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 429 Rate Limited

**User Message:** "Sorry, I encountered an error processing your request."

**Troubleshooting:**
1. Check Cloud Logging for correlation ID
2. Verify Agent Engine status
3. Check A2A gateway health

### 2. Timeout Errors

**Error Type:** `timeout`

**Causes:**
- Agent Engine slow response
- Network latency
- LLM processing delay

**User Message:** "Sorry, my request timed out. Please try again."

**Troubleshooting:**
1. Check `AGENT_ENGINE_TIMEOUT_SECONDS` setting
2. Review Agent Engine latency metrics
3. Consider increasing timeout for complex queries

### 3. Connection Errors

**Error Type:** `connection`

**Causes:**
- A2A gateway down
- Network partition
- DNS resolution failure

**User Message:** "Sorry, I'm having trouble connecting to my backend."

**Troubleshooting:**
1. Check A2A gateway health endpoint
2. Verify network connectivity
3. Check Cloud Run service status

### 4. Unknown Errors

**Error Type:** `unknown`

**Causes:**
- Unexpected exceptions
- Code bugs
- Malformed responses

**User Message:** "Sorry, something went wrong."

**Troubleshooting:**
1. Check full stack trace in Cloud Logging
2. Search by correlation ID
3. Review recent deployments

## Correlation ID

Every request is assigned a unique correlation ID (UUID v4) for end-to-end tracing.

### Log Search by Correlation ID

**Cloud Logging:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="slack-webhook"
jsonPayload.correlation_id="<UUID>"
```

### Log Fields

All error logs include:
- `correlation_id` - Request trace ID
- `error_type` - Category (http_status, timeout, connection, unknown)
- `attempt` - Retry attempt number
- Additional context fields

## Health Endpoint

The `/health` endpoint exposes resilience configuration:

```json
{
  "status": "healthy",
  "service": "slack-webhook",
  "version": "0.8.0",
  "resilience": {
    "timeout_seconds": 60,
    "retry_enabled": true,
    "max_retries": 1
  }
}
```

## Monitoring

### Key Metrics

1. **Error Rate by Type**
   - Track `error_type` distribution
   - Alert on spikes in any category

2. **Retry Rate**
   - Track requests with `attempt > 1`
   - High retry rate indicates backend issues

3. **Timeout Rate**
   - Track `error_type=timeout`
   - Adjust timeout if consistently high

4. **Latency P95/P99**
   - Monitor response times
   - Set timeout slightly above P99

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate | > 1% | > 5% |
| Timeout rate | > 0.5% | > 2% |
| Retry rate | > 5% | > 15% |
| P99 latency | > 50s | > 55s |

## Recovery Procedures

### High Error Rate

1. Check Agent Engine status in GCP Console
2. Verify A2A gateway is healthy
3. Check for recent deployments
4. Review error logs by correlation ID
5. Consider rollback if recent deployment

### High Timeout Rate

1. Check Agent Engine latency metrics
2. Increase `AGENT_ENGINE_TIMEOUT_SECONDS`
3. Check for LLM model issues
4. Review query complexity

### Connection Failures

1. Check A2A gateway health
2. Verify Cloud Run service is running
3. Check network/VPC configuration
4. Restart affected services

## Testing

### Run Error Handling Tests

```bash
pytest tests/slack_gateway/test_error_handling.py -v
```

### Simulate Failures

**Timeout Test (dev only):**
```bash
# Set very short timeout to trigger
AGENT_ENGINE_TIMEOUT_SECONDS=1 python -m pytest tests/
```

**Retry Test (dev only):**
```bash
# Mock 5xx responses to verify retry behavior
# See test_error_handling.py for examples
```

## Limitations

1. **No Circuit Breaker** - Retries are bounded but no circuit breaker pattern
2. **No Exponential Backoff** - Retries are immediate (acceptable for 1 retry)
3. **Correlation ID Not Propagated to Agent Engine** - API limitation
4. **Slack API Not Retried** - Only Agent Engine calls are retried

---
**Last Updated:** 2025-12-12
