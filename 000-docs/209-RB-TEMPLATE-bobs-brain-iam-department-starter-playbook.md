# Bob's Brain IAM Department Starter Playbook

**Date:** 2025-12-12
**Type:** Runbook
**Audience:** Platform Engineers, Agent Developers

## Overview

This playbook documents how to use `bobs-brain` as a template for creating new IAM (Intent Agent Model) department repositories.

## Quick Start

### 1. Export Template

```bash
# Clone bobs-brain (or navigate to existing clone)
cd /path/to/bobs-brain

# Export template to new directory
python scripts/export_iam_template.py /path/to/my-new-agents

# Navigate to new project
cd /path/to/my-new-agents
```

### 2. Initialize Git

```bash
git init
git add .
git commit -m "chore: initialize from IAM department template"
```

### 3. Replace Placeholders

Search and replace these placeholders:
- `{{PROJECT_ID}}` → Your GCP project ID
- `{{SPIFFE_ID}}` → Your agent SPIFFE ID (format: `spiffe://org/agent/name/env/region/version`)
- `{{ORG_NAME}}` → Your organization name
- `{{DATE}}` → Current date

### 4. Create Required Files

```bash
# VERSION file
echo "0.1.0" > VERSION

# CHANGELOG.md
cat > CHANGELOG.md << 'EOF'
# Changelog

## [Unreleased]

### Added
- Initial project setup from IAM department template

EOF

# requirements.txt
cat > requirements.txt << 'EOF'
google-cloud-aiplatform>=1.111
google-adk>=1.15.1
EOF

# README.md - customize for your project
# CLAUDE.md - copy and adapt from bobs-brain
```

## Template Mappings

| bobs-brain | Template | Purpose |
|------------|----------|---------|
| `agents/bob/` | `agents/foreman/` | Top-level orchestrator |
| `agents/iam_senior_adk_devops_lead/` | `agents/foreman/` | Department orchestrator |
| `agents/iam_*/` | `agents/specialists/` | Worker agents |
| `infra/terraform/` | `infra/terraform/` | Infrastructure as Code |
| `service/slack_webhook/` | `service/` | Cloud Run gateways (R3) |
| `.github/workflows/ci.yml` | `.github/workflows/ci-template.yml` | CI/CD pipeline |

## What Must Be Customized

### Required Customization

| Item | What to Change |
|------|----------------|
| Agent names | Rename `foreman/` to your orchestrator |
| System prompts | Update `FOREMAN_PROMPT` in agent.py |
| Terraform variables | Update project IDs, regions, etc. |
| GitHub secrets | Configure WIF, service accounts |
| CI workflow paths | Update for your project structure |

### Optional Customization

| Item | When to Change |
|------|----------------|
| Specialist agents | Add domain-specific workers |
| Tools | Add agent tools for your use case |
| Gateway type | Slack, A2A, or both |
| Memory wiring | Configure R5 based on requirements |

## What Can Be Reused As-Is

| Item | Notes |
|------|-------|
| Directory structure | Follows canonical pattern |
| Hard Mode rules | R1-R8 apply to all IAM repos |
| CI workflow structure | Jobs and gates pattern |
| Documentation format | NNN-CC-ABCD naming |
| Versioning script | `check_versioning.py` |
| Deploy script patterns | `deploy_inline_source.py` |

## Step-by-Step: Create First Agent

### 1. Customize Foreman

```python
# agents/foreman/agent.py

FOREMAN_PROMPT = """
You are the orchestrator for [YOUR PROJECT NAME].

Your responsibilities:
1. [Define your orchestrator's role]
2. [List capabilities]
3. [Define delegation rules]

Specialists available:
- specialist_one: [Description]
- specialist_two: [Description]
"""
```

### 2. Add First Specialist

```bash
mkdir -p agents/specialists/specialist_one
```

```python
# agents/specialists/specialist_one/agent.py

SPECIALIST_PROMPT = """
You are specialist_one, responsible for [SPECIFIC TASK].

Input schema:
- task: string (required)
- options: object (optional)

Output schema:
- result: string
- success: boolean
"""
```

### 3. Add AgentCard

```json
// agents/specialists/specialist_one/.well-known/agent-card.json
{
  "name": "specialist_one",
  "version": "0.1.0",
  "skills": [
    {
      "name": "primary_skill",
      "inputSchema": {"type": "object", "properties": {...}},
      "outputSchema": {"type": "object", "properties": {...}}
    }
  ]
}
```

## Deployment Flow

### Dev Deployment

1. Configure GitHub secrets for dev
2. Push to main branch
3. CI runs checks
4. Trigger manual deploy workflow
5. Verify in Cloud Console

### Stage/Prod Deployment

1. Complete dev testing
2. Update VERSION
3. Create release tag
4. Trigger stage workflow
5. Test in stage
6. Trigger prod workflow (requires approvals)

## Troubleshooting

### "Template source not found"

Run the export script from the bobs-brain repository root.

### "ADK not installed"

Install dependencies:
```bash
pip install google-cloud-aiplatform[adk,agent_engines]>=1.111
```

### CI failing on structure checks

Ensure all required directories exist:
```bash
mkdir -p 000-docs agents service infra scripts tests .github/workflows
```

## See Also

- `000-docs/6767-DR-TEMPLATE-iam-department-skeleton-standard.md`
- `000-docs/6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`
- Reference implementation: https://github.com/intent-solutions-io/bobs-brain

---
**Last Updated:** 2025-12-12
