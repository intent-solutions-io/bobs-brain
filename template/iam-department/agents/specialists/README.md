# Specialist Agents

This directory contains specialist (worker) agents for the IAM department.

## Pattern

Each specialist should:
1. Have a single, focused responsibility
2. Follow ADK lazy-loading pattern
3. Expose strict JSON input/output schemas
4. Be deterministic (no planning loops)

## Directory Structure

```
specialists/
├── specialist_one/
│   ├── __init__.py
│   ├── agent.py
│   └── README.md
├── specialist_two/
│   ├── __init__.py
│   ├── agent.py
│   └── README.md
└── ...
```

## Creating a New Specialist

1. Create directory: `mkdir specialists/my_specialist/`
2. Add `__init__.py` with version
3. Add `agent.py` with lazy-loading pattern
4. Add `agent-card.json` for A2A protocol
5. Add README.md with documentation

## Reference Specialists (from bobs-brain)

| Agent | Role |
|-------|------|
| iam_adk | ADK compliance checking |
| iam_issue | GitHub issue creation |
| iam_fix_plan | Fix planning |
| iam_fix_impl | Fix implementation |
| iam_qa | Testing and validation |
| iam_doc | Documentation |
| iam_cleanup | Repository hygiene |
| iam_index | Knowledge indexing |

## AgentCard Requirements

Each specialist must have an AgentCard defining:
- Skills with input/output JSON schemas
- Strict typing (no freeform text)
- Deterministic behavior specification

See `6767-DR-STND-agentcards-and-a2a-contracts.md` for details.
