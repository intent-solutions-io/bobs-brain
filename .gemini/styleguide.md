# Bob's Brain Code Style Guide

## Overview

This is a production-grade ADK (Agent Development Kit) agent department built on Google's Agent Development Kit and Vertex AI Agent Engine. All code must follow "Hard Mode" rules (R1-R8).

## Architecture Context

- **Three-tier architecture**: Bob (conversational) → Foreman (orchestrator) → Specialists (workers)
- **A2A Protocol**: Agents communicate via AgentCards and strict JSON contracts
- **Inline source deployment**: No serialization/pickle, source code deployed directly

## Hard Mode Rules (Non-Negotiable)

When reviewing code, flag violations of these rules:

1. **R1: ADK-Only** - No LangChain, CrewAI, or custom frameworks. Only `google-adk` imports.
2. **R2: Vertex AI Agent Engine** - No self-hosted runners
3. **R3: Gateway Separation** - Cloud Run proxies only, no Runner code in service/
4. **R4: CI-Only Deployments** - GitHub Actions with WIF, no manual gcloud commands
5. **R5: Dual Memory Wiring** - VertexAiSessionService + VertexAiMemoryBankService
6. **R6: Single Doc Folder** - All docs in `000-docs/` with NNN-CC-ABCD naming
7. **R7: SPIFFE ID Propagation** - In AgentCard, logs, headers
8. **R8: Drift Detection** - Runs first in CI, blocks violations

## Python Style

- Use lazy-loading App pattern (module-level `app`, not `agent`)
- Use `google-adk` imports exclusively
- Implement `after_agent_callback` for R5 compliance
- Type hints required for function signatures
- Docstrings for public functions

## Terraform Style

- Use modules over copy-pasted resources
- Keep env configs in `envs/dev`, `envs/stage`, `envs/prod`
- Consistent resource naming

## Security Focus

- No hardcoded secrets (use Secret Manager)
- Validate inputs at system boundaries
- No exposed credentials in logs
- SPIFFE IDs for agent identity

## Testing Requirements

- Unit tests for all agent logic
- AgentCard contract validation
- A2A protocol compliance tests

## Documentation

- All docs in `000-docs/` (R6)
- Format: `NNN-CC-ABCD-description.md`
- Categories: PP (Planning), AT (Architecture), AA (After-Action), DR (Reference)
