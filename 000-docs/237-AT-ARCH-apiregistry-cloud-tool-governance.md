# 237-AT-ARCH-apiregistry-cloud-tool-governance.md

**Document Type:** Architecture Design
**Status:** Proposed
**Created:** 2025-12-20
**Author:** Claude Code (Build Captain)

---

## Executive Summary

This document describes the integration of Google Cloud API Registry with Bob's Brain for **centralized tool governance**. The architecture separates MCP servers from agent code - agents discover tools at runtime via the registry, not at build time.

**Key Principle:** MCP servers are independent infrastructure, NOT part of the agent build.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE SEPARATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  bobs-brain/                        │  SEPARATE REPOS (not in bobs-brain)  │
│  ├── agents/                        │                                       │
│  │   ├── bob/                       │  mcp-repo-ops/                        │
│  │   ├── iam_senior.../             │  ├── Dockerfile                       │
│  │   └── iam_*/                     │  ├── server.py                        │
│  │       └── NO MCP SERVER CODE     │  └── deploys to Cloud Run             │
│  │                                  │                                       │
│  └── agents use:                    │  mcp-github/                          │
│      ApiRegistry.get_toolset()      │  ├── Dockerfile                       │
│      (runtime discovery)            │  ├── server.py                        │
│                                     │  └── deploys to Cloud Run             │
│                                     │                                       │
│  Deploys to: Agent Engine           │  Deploys to: Cloud Run                │
│  Build contains: Agent code only    │  Build contains: MCP server code only │
│                                     │                                       │
├─────────────────────────────────────┴───────────────────────────────────────┤
│                                                                             │
│                      CLOUD API REGISTRY (Console)                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Registered MCP Servers:                                              │   │
│  │                                                                      │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│  │  │ google-bigquery  │  │ mcp-repo-ops     │  │ mcp-github       │  │   │
│  │  │ (Google managed) │  │ (your Cloud Run) │  │ (your Cloud Run) │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│  │                                                                      │   │
│  │  IAM Controls: Which agents can access which MCP servers            │   │
│  │  Audit Logs: All tool discovery and invocation events               │   │
│  │  Approval Workflow: Security team approves new tools                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why This Separation Matters

### Traceability

| Concern | Without Registry | With Registry |
|---------|-----------------|---------------|
| "What tools can iam-adk access?" | Grep the code | Query the registry |
| "Who called create_issue at 3am?" | Parse Cloud Run logs | Registry audit log |
| "What changed in tool access?" | Git diff | Registry change history |
| "Is this agent authorized?" | Check code + IAM | Single IAM check |

**Two-layer audit trail:**
1. **Registry layer** - Tool discovery events (who requested what tools)
2. **MCP layer** - Tool execution events (what was actually called)

### Governance

| Concern | Without Registry | With Registry |
|---------|-----------------|---------------|
| Add new tool | Code change + deploy | Register + approve |
| Revoke tool access | Code change + deploy | Disable in registry (instant) |
| Emergency lockdown | Redeploy all agents | Toggle in console |
| Compliance audit | Reconstruct from git | Export from registry |

**Separation of duties:**
- **Security team** → Manages API Registry (approve/deny tools)
- **Infrastructure team** → Deploys MCP servers to Cloud Run
- **Agent team** → Uses `ApiRegistry.get_toolset()` (just consumes)

### Independent Lifecycles

```
MCP Server Update                    Agent Update
─────────────────                    ────────────
1. Fix bug in mcp-github             1. Update Bob's prompt
2. Push to mcp-github repo           2. Push to bobs-brain repo
3. Cloud Run redeploys               3. Agent Engine redeploys
4. Agents automatically get fix      4. No MCP server impact
   (no agent redeploy needed)
```

---

## What is Cloud API Registry?

Google's Cloud API Registry for Vertex AI Agent Builder provides:

- **Centralized tool governance** - Single registry for all agent tools
- **Dynamic MCP discovery** - Agents fetch approved tools at runtime
- **Admin-curated toolsets** - IT/admin controls which tools agents can access
- **Audit trail** - Track which agents use which tools
- **IAM integration** - Fine-grained access control

### The Runtime Flow

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Agent  │────▶│ API Registry │────▶│   IAM Check │────▶│  MCP Server  │
│ (Bob)   │     │              │     │             │     │ (Cloud Run)  │
└─────────┘     └──────────────┘     └─────────────┘     └──────────────┘
     │                 │                    │                    │
     │  get_toolset()  │                    │                    │
     │────────────────▶│                    │                    │
     │                 │ Check permissions  │                    │
     │                 │───────────────────▶│                    │
     │                 │      ✅ Allowed    │                    │
     │                 │◀───────────────────│                    │
     │   Tool handles  │                    │                    │
     │◀────────────────│                    │                    │
     │                 │                    │                    │
     │  invoke tool    │                    │                    │
     │─────────────────┼────────────────────┼───────────────────▶│
     │                 │                    │                    │
     │  result         │                    │                    │
     │◀────────────────┼────────────────────┼────────────────────│
     │                 │                    │                    │
     ▼                 ▼                    ▼                    ▼
  Audit Log        Audit Log           Audit Log            Audit Log
```

---

## Agent-Side Implementation

The agent code is minimal - it only discovers tools, never defines them:

```python
# agents/shared_tools/api_registry.py

from typing import Optional, Any, List
import logging
import os

logger = logging.getLogger(__name__)

_registry_instance: Optional[Any] = None


def get_api_registry():
    """
    Get or initialize the Cloud API Registry client.

    Lazy singleton pattern (6767-LAZY compliant).
    """
    global _registry_instance

    if _registry_instance is not None:
        return _registry_instance

    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        logger.warning("PROJECT_ID not set - ApiRegistry disabled")
        return None

    try:
        from google.adk.tools import ApiRegistry

        _registry_instance = ApiRegistry(
            project_id=project_id,
            header_provider=_get_header_provider()
        )
        logger.info(f"Initialized ApiRegistry for project: {project_id}")
        return _registry_instance

    except ImportError:
        logger.warning("ApiRegistry not available in this ADK version")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize ApiRegistry: {e}")
        return None


def _get_header_provider():
    """Get header provider for auth context propagation (R7 compliance)."""
    try:
        from google.auth import default
        from google.auth.transport.requests import Request

        credentials, _ = default()

        def header_provider() -> dict:
            credentials.refresh(Request())
            return {"Authorization": f"Bearer {credentials.token}"}

        return header_provider
    except Exception:
        return None


def get_tools_for_agent(agent_name: str) -> List[Any]:
    """
    Fetch all approved tools for a specific agent from the registry.

    The registry knows which MCP servers this agent can access based on IAM.
    Agent code does NOT hardcode tool lists.

    Args:
        agent_name: The agent requesting tools (e.g., "iam-adk", "bob")

    Returns:
        List of tool handles from approved MCP servers
    """
    registry = get_api_registry()
    if registry is None:
        logger.warning(f"Registry unavailable for {agent_name} - no tools loaded")
        return []

    try:
        # Registry returns tools this agent is authorized to use
        # Based on IAM bindings, not hardcoded in agent code
        tools = registry.get_agent_tools(agent_name)
        logger.info(f"Loaded {len(tools)} tools for {agent_name} from registry")
        return tools
    except Exception as e:
        logger.error(f"Failed to get tools for {agent_name}: {e}")
        return []
```

### Agent Tool Profile (New Pattern)

```python
# agents/shared_tools/__init__.py

from .api_registry import get_tools_for_agent


def get_bob_tools() -> List[Any]:
    """
    Bob's tools - fetched from registry at runtime.

    NO HARDCODED TOOL DEFINITIONS.
    Registry + IAM determines what Bob can access.
    """
    return get_tools_for_agent("bob")


def get_iam_adk_tools() -> List[Any]:
    """iam-adk tools - fetched from registry."""
    return get_tools_for_agent("iam-adk")


def get_iam_issue_tools() -> List[Any]:
    """iam-issue tools - fetched from registry."""
    return get_tools_for_agent("iam-issue")

# ... etc for all agents
```

---

## MCP Server Infrastructure (Separate Repos)

MCP servers live in their own repositories, deployed independently:

### Example: mcp-repo-ops

```
mcp-repo-ops/                    # SEPARATE REPO
├── Dockerfile
├── requirements.txt
├── server.py                    # MCP server implementation
├── tools/
│   ├── search_codebase.py
│   ├── get_file_contents.py
│   ├── analyze_dependencies.py
│   └── check_patterns.py
├── terraform/
│   └── cloud_run.tf            # Deploys to Cloud Run
└── .github/workflows/
    └── deploy.yml              # CI/CD for this server only
```

### MCP Server Registration (Terraform)

```hcl
# mcp-repo-ops/terraform/registry.tf

resource "google_vertex_ai_mcp_server" "repo_ops" {
  project  = var.project_id
  location = "global"

  display_name = "mcp-repo-ops"
  description  = "Repository operations for Bob's Brain agents"

  server_config {
    cloud_run_service = google_cloud_run_service.mcp_repo_ops.name
  }

  # IAM bindings - which agents can use this server
  # Managed separately by security team
}

resource "google_cloud_run_service" "mcp_repo_ops" {
  name     = "mcp-repo-ops"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/mcp-repo-ops:latest"
      }
    }
  }
}
```

---

## Planned MCP Servers

| Server | Purpose | Tools | Priority |
|--------|---------|-------|----------|
| `mcp-repo-ops` | Repository operations | search_codebase, get_file, analyze_deps, check_patterns | High |
| `mcp-github` | GitHub integration | create_issue, create_pr, list_workflows, get_reviews | High |
| `mcp-adk-analyzer` | ADK compliance | check_hardmode, validate_agent, lint_prompts | Medium |
| Google BigQuery | Data operations | execute_sql, list_datasets, get_schema | Use Google's |

---

## Hard Mode Compliance

| Rule | Status | Notes |
|------|--------|-------|
| R1: ADK-Only | ✅ | Uses `google.adk.tools.ApiRegistry` |
| R3: Gateway Separation | ✅ | MCP servers on Cloud Run, not in Agent Engine |
| R4: CI-Only Deployments | ✅ | MCP servers deploy via Terraform, agents deploy via CI |
| R5: Dual Memory | ✅ | No impact on memory wiring |
| R7: SPIFFE ID | ✅ | Header provider propagates auth context |
| R8: Drift Detection | ✅ | Registry is source of truth, not code |

**R4 Note:** Registry approval happens in Console, but MCP server deployment is Terraform. Future: registry-as-code.

---

## Implementation Phases

### Phase 1: Agent-Side Foundation
- [ ] Create `agents/shared_tools/api_registry.py`
- [ ] Add `get_api_registry()` singleton
- [ ] Add `get_tools_for_agent()` function
- [ ] Update tool profiles to use registry
- [ ] Unit tests (mock registry)
- [ ] Fallback to empty tools if registry unavailable

### Phase 2: First MCP Server (mcp-repo-ops)
- [ ] Create `mcp-repo-ops` repository (separate from bobs-brain)
- [ ] Implement MCP server with search_codebase tool
- [ ] Deploy to Cloud Run via Terraform
- [ ] Register in API Registry
- [ ] Configure IAM for iam-adk access
- [ ] Integration test

### Phase 3: GitHub MCP Server
- [ ] Create `mcp-github` repository
- [ ] Implement create_issue, create_pr tools
- [ ] Deploy and register
- [ ] Configure IAM for iam-issue, iam-fix-impl

### Phase 4: Migration Complete
- [ ] Remove static tool definitions from agents/
- [ ] All tools come from registry
- [ ] Add registry health check to ARV gates
- [ ] Document governance procedures

---

## Testing Strategy

### Unit Tests (in bobs-brain)

```python
# tests/unit/test_api_registry.py

def test_registry_unavailable_returns_empty():
    """Without registry, agents should get empty tools (not crash)."""
    with patch.dict(os.environ, {}, clear=True):
        tools = get_tools_for_agent("bob")
        assert tools == []

def test_registry_error_returns_empty():
    """On registry error, should degrade gracefully."""
    with patch("google.adk.tools.ApiRegistry", side_effect=Exception("boom")):
        tools = get_tools_for_agent("iam-adk")
        assert tools == []
```

### Integration Tests (per MCP server repo)

```python
# mcp-repo-ops/tests/test_server.py

def test_search_codebase_returns_results():
    """MCP server should return search results."""
    response = client.call_tool("search_codebase", {"query": "def agent"})
    assert response.results is not None
```

---

## References

- [Cloud API Registry](https://cloud.google.com/vertex-ai/docs/agent-builder/api-registry) (when public)
- [ADK Tools Documentation](https://google.github.io/adk-docs/tools/)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- Bob's Brain Hard Mode Rules: `000-docs/6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-20 | MCP servers in separate repos | Clean separation, independent lifecycles, different teams |
| 2025-12-20 | Registry-first tool discovery | Governance, traceability, audit compliance |
| 2025-12-20 | No hardcoded tool lists | Registry + IAM is source of truth |
| 2025-12-20 | Graceful degradation | Agents work (with no tools) if registry down |
| 2025-12-20 | Start with mcp-repo-ops | High value, needed by multiple specialists |
