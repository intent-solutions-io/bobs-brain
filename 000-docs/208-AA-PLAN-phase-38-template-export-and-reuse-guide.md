# Phase 38: Template Export & Reuse Guide

**Date:** 2025-12-12
**Status:** In Progress
**Branch:** `feature/phase-38-template-export-and-reuse`

## Objective

Create a reusable template skeleton that captures the IAM department pattern (foreman + specialists, CI, docs, infra) for use in new repositories like `iam1-intent-agent-model-vertex-ai`.

## Goals

1. Add `template/iam-department/` skeleton with representative structure
2. Create export helper script for copying template to new projects
3. Document usage with step-by-step guide
4. Provide 6767-series standard for template compliance

## Non-Goals

- Rename this repo
- Auto-create other repos
- Full code duplication (use references instead)

## Template Contents

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

## Implementation Steps

1. [ ] Create `template/iam-department/` directory structure
2. [ ] Add skeleton files with TODOs and references
3. [ ] Create `scripts/export_iam_template.py`
4. [ ] Add playbook doc: `000-docs/209-RB-TEMPLATE-bobs-brain-iam-department-starter-playbook.md`
5. [ ] Add 6767 standard: `000-docs/6767-DR-TEMPLATE-iam-department-skeleton-standard.md`

## Export Script Behavior

```bash
python scripts/export_iam_template.py /path/to/destination

# Copies template/iam-department/ to destination
# Excludes: .git, __pycache__, *.pyc
# Prints next steps for customization
```

## Success Criteria

- [ ] Template directory exists with minimal skeleton
- [ ] Export script works and prints clear instructions
- [ ] Playbook documents how to use template
- [ ] 6767 standard defines required structure

---
**Last Updated:** 2025-12-12
