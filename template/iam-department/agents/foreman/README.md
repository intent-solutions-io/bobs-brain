# Foreman Agent

The Foreman is the orchestrator for this IAM department. It receives tasks and delegates to specialist agents.

## Quick Start

```python
from agents.foreman.agent import get_agent

agent = get_agent()
```

## Structure

```
foreman/
├── __init__.py      # Package init with version
├── agent.py         # Main agent definition (entrypoint)
├── tools/           # Agent tools (TODO)
│   └── __init__.py
└── prompts/         # System prompts (TODO)
    └── main.txt
```

## Configuration

Environment variables:
- `DEPLOYMENT_ENV` - Environment (dev/stage/prod)
- `AGENT_SPIFFE_ID` - Agent identity

## Reference

See bobs-brain implementation:
- `agents/iam_senior_adk_devops_lead/`

## TODO

1. [ ] Customize system prompt
2. [ ] Add specialist delegation tools
3. [ ] Configure A2A wiring
4. [ ] Add AgentCard for A2A protocol
