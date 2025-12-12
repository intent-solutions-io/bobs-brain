# Getting Started with Bob's Brain

Welcome to Bob's Brain - a production-grade ADK agent department for software engineering automation.

## Prerequisites

- **Python:** 3.12 or higher
- **Git:** For version control
- **GCP Access:** For Agent Engine deployment (optional for local dev)
- **Make:** For running project tasks

## Quick Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/intent-solutions-io/bobs-brain.git
cd bobs-brain

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Run drift detection (must pass)
make check-all

# Run tests
pytest tests/unit/ -v

# Check agent readiness
make check-arv-minimum
```

Expected output:
```
✅ All drift detection checks passed
✅ All ARV checks passed
```

### 3. Local Development

```bash
# Run a specific agent locally (development mode)
python -c "from agents.bob.agent import app; print(app)"

# Run the test suite with coverage
pytest --cov=agents --cov-report=term-missing

# Format code
make format

# Lint code
make lint
```

## Project Structure

```
bobs-brain/
├── agents/                    # Agent implementations
│   ├── bob/                   # Main orchestrator agent
│   ├── iam_*/                 # Specialist agents (8)
│   ├── config/                # Configuration modules
│   ├── tools/                 # Shared tools
│   └── shared_contracts.py    # Data contracts
├── service/                   # Gateway services
│   ├── a2a_gateway/           # A2A protocol gateway
│   └── slack_webhook/         # Slack integration
├── infra/terraform/           # Infrastructure as Code
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
├── templates/                 # Reusable templates
└── 000-docs/                  # Documentation
```

## Key Commands

| Command | Description |
|---------|-------------|
| `make check-all` | Run all quality checks |
| `make test` | Run test suite |
| `make lint` | Check code style |
| `make format` | Format code |
| `make check-arv-minimum` | Verify agent readiness |
| `make check-rag-readiness` | Verify RAG configuration |

## Architecture Overview

Bob's Brain uses a three-tier agent architecture:

```
User (Slack) → Bob (Orchestrator)
                    ↓ A2A Protocol
              Foreman (iam-senior-adk-devops-lead)
                    ↓ A2A Protocol
              Specialists (iam-adk, iam-issue, iam-qa, ...)
```

**Key Concepts:**
- **Bob:** Conversational AI that understands user requests
- **Foreman:** Orchestrates workflows across specialists
- **Specialists:** Execute specific tasks (auditing, issue creation, QA)

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the patterns in existing code. Key rules:
- Use ADK patterns only (R1)
- Keep gateways stateless (R3)
- All deployments via CI (R4)

### 3. Run Checks

```bash
make check-all
pytest tests/
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat(scope): description"
git push -u origin feature/your-feature-name
```

### 5. Create Pull Request

```bash
gh pr create --title "Your PR Title" --body "Description"
```

## Deployment

Deployments happen automatically via GitHub Actions:

| Environment | Trigger | Workflow |
|-------------|---------|----------|
| Dev | Push to `main` | `ci.yml` |
| Staging | Manual | `deploy-staging.yml` |
| Production | Manual | `terraform-prod.yml` |

For local development, you don't need to deploy - tests run locally.

## Documentation

- **This Guide:** Getting started basics
- **CLAUDE.md:** AI assistant guidance
- **CONTRIBUTING.md:** How to contribute
- **000-docs/:** All documentation (100+ files)

Key documentation:
- `000-docs/DEVOPS-QUICK-REFERENCE.md` - Operations reference
- `000-docs/6767-DR-STND-*.md` - Standards and specifications
- `000-docs/6767-RB-OPS-*.md` - Runbooks

## Troubleshooting

### Common Issues

**ModuleNotFoundError:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Drift Detection Fails:**
```bash
# Check what's failing
bash scripts/ci/check_nodrift.sh
# Fix violations (usually import issues)
```

**Tests Fail:**
```bash
# Run verbose to see details
pytest tests/ -v --tb=short
```

### Getting Help

1. Check existing documentation in `000-docs/`
2. Review error messages carefully
3. Search for similar patterns in codebase
4. Create GitHub issue if stuck

## Next Steps

1. Read `CLAUDE.md` for architecture context
2. Explore `agents/bob/` to understand the main agent
3. Run the test suite to understand coverage
4. Make a small change to get familiar with the workflow

---

**Version:** 1.0.0
**Last Updated:** 2025-12-12
