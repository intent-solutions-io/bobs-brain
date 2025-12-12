# New Engineer Quickstart

**Date:** 2025-12-11
**Audience:** Engineers new to bobs-brain repository

## What Is This Repo?

**Bob's Brain** is a production-grade **ADK agent department** - a multi-agent system built on:
- Google Agent Development Kit (ADK)
- Vertex AI Agent Engine
- Cloud Run gateways

It serves as:
1. A working Slack AI assistant
2. The canonical reference implementation for multi-agent departments
3. A template for future agent repositories

## High-Level Architecture

```
User (Slack)
    |
    v
Bob (Orchestrator LLM Agent)
    |
    v [A2A Protocol]
Foreman (iam-senior-adk-devops-lead)
    |
    v [A2A Protocol]
Specialists (iam-adk, iam-issue, iam-qa, etc.)
```

**Key Concepts:**
- **Bob**: Conversational interface, delegates complex work
- **Foreman**: Orchestrates workflows across specialists
- **Specialists**: Execute specific tasks (compliance checks, issue creation, etc.)
- **A2A Protocol**: Agent-to-agent communication via AgentCards

## Repository Structure

```
bobs-brain/
├── agents/              # ADK agent implementations
│   ├── bob/             # Main orchestrator
│   ├── iam-senior-adk-devops-lead/  # Foreman
│   ├── iam_adk/         # ADK compliance specialist
│   ├── iam_issue/       # Issue creation specialist
│   └── shared_contracts.py  # Shared Pydantic models
│
├── service/             # Cloud Run gateways
│   └── slack-webhook/   # Slack -> Bob gateway
│
├── infra/terraform/     # Infrastructure as Code
│   ├── envs/            # dev, stage, prod configs
│   └── modules/         # Reusable TF modules
│
├── scripts/             # Automation scripts
│   ├── deploy_inline_source.py
│   └── promote_agent_engine_config.py
│
├── tests/               # Unit and integration tests
│
├── config/              # Configuration files
│   └── agent_engine_envs.yaml  # Engine ID mapping
│
├── 000-docs/            # ALL documentation (flat)
│
├── CLAUDE.md            # AI assistant guidance
├── VERSION              # Current version
└── Makefile             # Development commands
```

## First Commands

After cloning, run these to verify your setup:

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run all quality checks
make check-all

# 3. Run unit tests
make test

# 4. Check A2A contracts
make check-a2a-contracts

# 5. Run ARV department checks
make arv-department
```

## Where To Look First

1. **CLAUDE.md** - AI assistant guidance, TL;DR section has quick reference
2. **000-docs/191-INDEX-bobs-brain-reference-map.md** - Master doc index
3. **000-docs/6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md** - Hard Mode rules (R1-R8)

## Key Rules (The "Don'ts")

1. **Don't use gcloud CLI for deployments** - All deploys via Terraform/CI (R4)
2. **Don't create nested folders in 000-docs/** - Keep flat (R6)
3. **Don't import non-ADK frameworks** - No LangChain, CrewAI (R1)
4. **Don't skip ARV gates** - Always validate before deploy
5. **Don't edit secrets directly** - Use Secret Manager

## Common Tasks

### Add a New Agent

1. Create directory: `agents/<agent-name>/`
2. Add `agent.py`, `app.py`, `a2a_card.py`
3. Add to `agents/__init__.py`
4. Create AgentCard tests
5. Run `make check-a2a-contracts`

### Deploy to Dev

```bash
# Validate first
make check-inline-deploy-ready

# Dry run
make deploy-inline-dry-run

# Actual deploy (requires GCP auth)
make deploy-inline-dev-execute
```

### Create Documentation

1. Find next doc number: `ls 000-docs/*.md | tail -5`
2. Use format: `NNN-CC-ABCD-description.md`
3. Categories: AA (AAR), AT (Architecture), DR (Reference), RB (Runbook)

## Getting Help

- **Docs**: Check `000-docs/` index first
- **Standards**: Search `000-docs/6767-*`
- **CLAUDE.md**: Detailed guidance for AI assistants
- **Slack**: #bobs-brain channel

## Next Steps

1. Read CLAUDE.md (especially TL;DR section)
2. Explore `agents/bob/` to see agent structure
3. Run `make help` to see all available commands
4. Check latest AAR in `000-docs/` for current status

---
**Last Updated:** 2025-12-11
