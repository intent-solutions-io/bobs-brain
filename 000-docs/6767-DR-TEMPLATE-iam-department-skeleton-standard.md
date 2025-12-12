# 6767: IAM Department Skeleton Standard

**Date:** 2025-12-12
**Type:** Standard
**Status:** Active
**Applies to:** All IAM department repositories

## Overview

This standard defines the required structure for IAM (Intent Agent Model) department repositories. It ensures consistency across all agent department implementations and enables tooling interoperability.

## Required Directory Structure

```
.
├── 000-docs/                    # Documentation (R6)
│   ├── NNN-CC-ABCD-*.md        # Numbered documents
│   └── 6767-*.md               # Standards (copied from bobs-brain)
├── agents/                      # ADK agents (R1)
│   ├── {orchestrator}/         # Top-level orchestrator
│   │   ├── __init__.py
│   │   ├── agent.py            # Entrypoint
│   │   └── .well-known/        # AgentCard
│   │       └── agent-card.json
│   └── {specialists}/          # Worker agents
│       └── ...
├── infra/                       # Infrastructure
│   └── terraform/              # Terraform IaC
│       ├── main.tf
│       ├── variables.tf
│       └── envs/               # Environment configs
├── service/                     # Cloud Run gateways (R3)
│   └── ...
├── scripts/                     # Utility scripts
│   └── ...
├── tests/                       # Test suites
│   ├── unit/
│   └── integration/
└── .github/                     # CI/CD
    └── workflows/
        └── ci.yml              # Main CI workflow
```

## Required Files

### Root Level

| File | Purpose | Required |
|------|---------|----------|
| `README.md` | Project overview | Yes |
| `CLAUDE.md` | Claude Code guidance | Yes |
| `VERSION` | SemVer version | Yes |
| `CHANGELOG.md` | Release notes | Yes |
| `requirements.txt` | Python dependencies | Yes |
| `Makefile` | Common commands | Yes |
| `.gitignore` | Git ignore rules | Yes |

### Agent Files

Each agent must have:

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization |
| `agent.py` | Agent definition with entrypoint |
| `.well-known/agent-card.json` | A2A protocol AgentCard |

### CI Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Main CI workflow |
| `scripts/ci/check_nodrift.sh` | Drift detection (R8) |

## Naming Conventions

### Directories

- Use lowercase with underscores: `agent_name/`
- Orchestrators: `foreman/`, `orchestrator/`, or domain-specific name
- Specialists: `iam_*/` or domain-specific prefixes

### Documents (R6)

Format: `NNN-CC-ABCD-description.md`

- `NNN` = Sequential number (001-999)
- `CC` = Category (AA, AT, DR, PP, etc.)
- `ABCD` = 4-letter document type

### Versions

Format: `MAJOR.MINOR.PATCH` (SemVer)

- VERSION file: `0.1.0` (no `v` prefix)
- Git tags: `v0.1.0` (with `v` prefix)

## Hard Mode Rules Reference

All IAM department repos must comply with:

| Rule | Description |
|------|-------------|
| R1 | ADK-only (no LangChain, CrewAI) |
| R2 | Vertex AI Agent Engine runtime |
| R3 | Gateway separation (Cloud Run proxies) |
| R4 | CI-only deployments |
| R5 | Dual memory wiring |
| R6 | Single doc folder (`000-docs/`) |
| R7 | SPIFFE ID propagation |
| R8 | Drift detection |

See: `6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`

## Validation

### Structure Check

```bash
# Required directories
for dir in 000-docs agents infra service scripts tests .github; do
  test -d "$dir" || echo "Missing: $dir"
done

# Required files
for file in README.md CLAUDE.md VERSION CHANGELOG.md requirements.txt Makefile; do
  test -f "$file" || echo "Missing: $file"
done
```

### Agent Check

```bash
# Each agent directory should have:
for agent_dir in agents/*/; do
  test -f "${agent_dir}__init__.py" || echo "Missing: ${agent_dir}__init__.py"
  test -f "${agent_dir}agent.py" || echo "Missing: ${agent_dir}agent.py"
done
```

## Template Export

Use the export script from bobs-brain:

```bash
python scripts/export_iam_template.py /path/to/new-project
```

This creates a compliant skeleton that can be customized.

## Compliance Verification

CI should verify structure compliance:

```yaml
# .github/workflows/ci.yml
- name: Verify 6767 structure compliance
  run: |
    # Check required directories
    test -d 000-docs/ || exit 1
    test -d agents/ || exit 1
    # ... etc
```

## Exceptions

Document any exceptions in `000-docs/` with category `AA` (After-Action):

- Why the exception is needed
- Risk assessment
- Remediation plan

## See Also

- `6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`
- `6767-DR-STND-document-filing-system-standard-v3.md`
- `6767-DR-STND-agentcards-and-a2a-contracts.md`
- `209-RB-TEMPLATE-bobs-brain-iam-department-starter-playbook.md`

---
**Last Updated:** 2025-12-12
