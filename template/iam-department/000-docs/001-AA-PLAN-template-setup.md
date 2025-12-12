# Template Setup Plan

**Date:** {{DATE}}
**Status:** In Progress
**Branch:** `main`

## Objective

Set up a new IAM department repository using the bobs-brain template.

## Checklist

### 1. Repository Setup
- [ ] Clone or export template
- [ ] Initialize git repository
- [ ] Configure remote origin
- [ ] Create initial branch structure

### 2. Configuration
- [ ] Replace all `{{PLACEHOLDER}}` values
- [ ] Update `VERSION` file
- [ ] Create `CHANGELOG.md`
- [ ] Configure `.env.example`

### 3. Agent Setup
- [ ] Rename foreman to match your use case
- [ ] Define specialist agent roles
- [ ] Create AgentCards for A2A protocol
- [ ] Implement agent logic

### 4. Infrastructure
- [ ] Update Terraform variables
- [ ] Configure WIF authentication
- [ ] Set up GitHub secrets
- [ ] Create GCP projects (dev/stage/prod)

### 5. CI/CD
- [ ] Test CI workflow locally
- [ ] Verify drift detection
- [ ] Configure environment protection

### 6. Documentation
- [ ] Update README.md
- [ ] Create CLAUDE.md
- [ ] Document agent architecture

## Dependencies

- GCP project with Vertex AI enabled
- GitHub repository with Actions enabled
- Service account with appropriate permissions
- WIF (Workload Identity Federation) configured

## Next Steps

After completing setup, create your first AAR:
- `002-AA-REPT-template-first-deploy.md`

---
**Template Source:** bobs-brain
