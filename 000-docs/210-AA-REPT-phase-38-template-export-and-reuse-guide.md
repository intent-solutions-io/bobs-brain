# Phase 38: Template Export & Reuse Guide - AAR

**Date:** 2025-12-12
**Status:** Complete
**Branch:** `feature/phase-38-template-export-and-reuse`

## Summary

Created a reusable IAM department template skeleton under `template/iam-department/` with export tooling and comprehensive documentation. This enables creating new agent department repositories quickly while following established patterns.

## What Was Built

### 1. Template Skeleton

**Directory:** `template/iam-department/`

Structure created:
```
template/iam-department/
├── 000-docs/
│   ├── 000-README-template-iam-department.md
│   ├── 001-AA-PLAN-template-setup.md
│   └── 002-AA-REPT-template-first-deploy.md
├── agents/
│   ├── foreman/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── README.md
│   └── specialists/
│       └── README.md
├── infra/
│   └── terraform/
│       └── README.md
├── service/
│   └── README-gateway-pattern.md
├── scripts/
│   └── README-scripts.md
├── tests/
│   └── README.md
└── .github/
    └── workflows/
        └── ci-template.yml
```

### 2. Export Script

**File:** `scripts/export_iam_template.py`

Features:
- Copies template to destination directory
- Excludes `.git`, `__pycache__`, `*.pyc`, etc.
- Supports `--force` to overwrite existing
- Prints clear next steps for customization

Usage:
```bash
python scripts/export_iam_template.py /path/to/new-project
```

### 3. Documentation

**Files created:**
- `000-docs/209-RB-TEMPLATE-bobs-brain-iam-department-starter-playbook.md` - Step-by-step usage guide
- `000-docs/6767-DR-TEMPLATE-iam-department-skeleton-standard.md` - Required structure standard

## Files Changed

| File | Action |
|------|--------|
| `template/iam-department/` | Created directory tree |
| `template/iam-department/000-docs/*.md` | Created (3 files) |
| `template/iam-department/agents/foreman/*` | Created (3 files) |
| `template/iam-department/agents/specialists/README.md` | Created |
| `template/iam-department/infra/terraform/README.md` | Created |
| `template/iam-department/service/README-gateway-pattern.md` | Created |
| `template/iam-department/scripts/README-scripts.md` | Created |
| `template/iam-department/tests/README.md` | Created |
| `template/iam-department/.github/workflows/ci-template.yml` | Created |
| `scripts/export_iam_template.py` | Created |
| `000-docs/208-AA-PLAN-phase-38-template-export-and-reuse-guide.md` | Created |
| `000-docs/209-RB-TEMPLATE-bobs-brain-iam-department-starter-playbook.md` | Created |
| `000-docs/6767-DR-TEMPLATE-iam-department-skeleton-standard.md` | Created |
| `000-docs/210-AA-REPT-phase-38-template-export-and-reuse-guide.md` | Created |

## Design Decisions

### Minimal Template Approach

The template contains:
- Directory structure with README files
- Skeleton foreman agent with lazy-loading pattern
- CI workflow with TODO markers
- References back to bobs-brain for full implementation

**Rationale:** Easier to customize from minimal skeleton than strip down full implementation.

### Placeholder Strategy

Using `{{PLACEHOLDER}}` format for:
- `{{PROJECT_ID}}`
- `{{SPIFFE_ID}}`
- `{{DATE}}`
- `{{ORG_NAME}}`

**Rationale:** Easy to find and replace, clearly marked as needing customization.

### Export vs Copy

Created dedicated export script rather than simple copy because:
- Excludes unnecessary files (`.git`, cache, etc.)
- Prints customization instructions
- Can be extended with more features later

## Usage

### Export Template

```bash
cd /path/to/bobs-brain
python scripts/export_iam_template.py /path/to/my-new-agents
```

### Initialize New Project

```bash
cd /path/to/my-new-agents
git init
git add .
git commit -m "chore: initialize from IAM department template"

# Replace placeholders
# Create required files (VERSION, README.md, etc.)
# Configure infrastructure
```

## Limitations

- Template contains stubs/TODOs, not full implementation
- User must copy relevant scripts from bobs-brain manually
- CI workflow requires customization before use

## Next Steps

1. Use template to create `iam1-intent-agent-model-vertex-ai`
2. Refine template based on usage feedback
3. Consider adding more complete agent stubs
4. Add template versioning

---
**Last Updated:** 2025-12-12
