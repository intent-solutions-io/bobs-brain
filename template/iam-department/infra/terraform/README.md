# Terraform Infrastructure

This directory contains Terraform configuration for deploying IAM department infrastructure.

## Structure

```
terraform/
├── main.tf              # Main configuration
├── variables.tf         # Variable definitions
├── outputs.tf           # Output values
├── modules/             # Reusable modules
│   ├── agent_engine/    # Agent Engine deployment
│   └── gateway/         # Cloud Run gateway (R3)
└── envs/                # Environment-specific configs
    ├── dev.tfvars
    ├── stage.tfvars
    └── prod.tfvars
```

## Required Variables

| Variable | Description |
|----------|-------------|
| `project_id` | GCP project ID |
| `region` | GCP region |
| `environment` | Environment name (dev/stage/prod) |
| `agent_spiffe_id` | Agent SPIFFE ID |

## Quick Start

```bash
# Initialize
terraform init

# Plan for dev
terraform plan -var-file="envs/dev.tfvars"

# Apply (via CI only - R4)
# terraform apply -var-file="envs/dev.tfvars"
```

## Hard Mode Rules

- **R3:** Gateway separation - Cloud Run gateways only, no Agent Engine in service/
- **R4:** CI-only deployments - Never run terraform apply locally
- **R7:** SPIFFE ID propagation - Include in all resources

## Reference

See bobs-brain implementation:
- `infra/terraform/`
- `infra/terraform/modules/slack_bob_gateway/`

## TODO

1. [ ] Copy modules from bobs-brain
2. [ ] Update variables for your project
3. [ ] Configure backend state
4. [ ] Set up WIF authentication
