# Gateway Pattern (R3 Compliance)

This directory contains Cloud Run gateway services that proxy requests to Agent Engine.

## R3: Gateway Separation

**Rule:** Cloud Run gateways in `service/` MUST NOT contain Agent Engine Runner code.

```
✅ ALLOWED in service/:
- HTTP request handlers
- Slack webhook handlers
- A2A protocol gateways
- Request validation
- Authentication/authorization

❌ NOT ALLOWED in service/:
- ADK agent code
- Direct LLM calls
- Agent Engine Runner
- Business logic
```

## Gateway Types

### Slack Gateway
Handles Slack webhook events and forwards to Agent Engine:
```
Slack → Cloud Run → Agent Engine → Response → Slack
```

### A2A Gateway
Handles agent-to-agent communication:
```
Agent A → A2A Gateway → Agent Engine (Agent B)
```

## Implementation Pattern

```python
# service/slack_webhook/main.py

from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def handle_slack_event():
    # Validate request
    # Parse event
    # Forward to Agent Engine
    response = call_agent_engine(event)
    # Return response to Slack
    return response
```

## Reference

See bobs-brain implementation:
- `service/slack_webhook/`
- `service/a2a_gateway/`

## TODO

1. [ ] Create Slack webhook handler
2. [ ] Create A2A gateway if needed
3. [ ] Configure Cloud Run deployment
4. [ ] Set up health checks
