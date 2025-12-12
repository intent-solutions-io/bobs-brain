# Scripts Directory

This directory contains utility scripts for the IAM department.

## Required Scripts

Based on bobs-brain patterns, consider adding:

| Script | Purpose |
|--------|---------|
| `check_versioning.py` | Validate VERSION and tags |
| `check_arv_minimum.py` | ARV minimum requirements |
| `check_inline_deploy_ready.py` | Deployment readiness |
| `deploy_inline_source.py` | Agent Engine deployment |
| `check_a2a_contracts.py` | AgentCard validation |

## Script Patterns

### Validation Scripts
- Exit code 0 = success
- Exit code 1 = validation failure
- Clear error messages
- Support `--verbose` flag

### Deployment Scripts
- Support `--dry-run` flag
- Require explicit `--execute` for real deployments
- Log all actions

## CI Integration

Scripts should be callable via Make targets:

```makefile
check-arv-minimum:
	python scripts/check_arv_minimum.py

deploy-dry-run:
	python scripts/deploy_inline_source.py --dry-run
```

## Reference

Copy scripts from bobs-brain as needed:
- `scripts/check_versioning.py`
- `scripts/check_arv_minimum.py`
- `scripts/deploy_inline_source.py`

## TODO

1. [ ] Copy relevant scripts from bobs-brain
2. [ ] Update project-specific paths
3. [ ] Add to Makefile
4. [ ] Test in CI
