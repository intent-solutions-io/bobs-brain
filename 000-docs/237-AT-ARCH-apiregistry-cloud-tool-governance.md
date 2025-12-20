# 237-AT-ARCH-apiregistry-cloud-tool-governance.md

**Document Type:** Architecture Design
**Status:** Proposed
**Created:** 2025-12-20
**Author:** Claude Code (Build Captain)

---

## Overview

This document describes the integration of Google Cloud API Registry with Bob's Brain for centralized tool governance. API Registry enables dynamic discovery and management of MCP (Model Context Protocol) servers across the agent department.

## Background

### What is Cloud API Registry?

Google's Cloud API Registry for Vertex AI Agent Builder provides:
- **Centralized tool governance** - Single registry for all agent tools
- **Dynamic MCP discovery** - Agents fetch approved tools at runtime
- **Admin-curated toolsets** - IT/admin controls which tools agents can access
- **Audit trail** - Track which agents use which tools

### Why Integrate?

Current state (`agents/shared_tools/`):
- Tools are statically imported at agent creation time
- Each agent has hardcoded tool profiles in `__init__.py`
- No central governance of what tools are available
- MCP servers require manual URL configuration

With API Registry:
- Tools can be added/removed without code changes
- Central dashboard for tool approval/revocation
- Dynamic discovery of new MCP capabilities
- Consistent tool access patterns across department

---

## Current Architecture

### Tool Layer Structure

```
agents/shared_tools/
├── __init__.py          # Tool profiles per agent (BOB_TOOLS, FOREMAN_TOOLS, etc.)
├── adk_builtin.py       # ADK built-in tools (GoogleSearch, CodeExecution, BigQuery)
├── custom_tools.py      # Domain-specific tools (analysis, delegation, etc.)
└── vertex_search.py     # Vertex AI Search integration
```

### Tool Profile Pattern

Each agent gets a curated tool list:

```python
def get_bob_tools() -> List[Any]:
    """Bob's tool profile - broad access."""
    tools = []
    tools.append(get_google_search_tool())
    tools.extend(get_adk_docs_tools())
    tools.append(get_bob_vertex_search_tool())
    return tools
```

**Problem:** Static at import time. Adding new tools requires code changes.

---

## Proposed Architecture

### Phase 1: Foundation (Non-Breaking)

Add ApiRegistry initialization alongside existing tools:

```python
# agents/shared_tools/api_registry.py

from typing import Optional, Any
import logging
import os

logger = logging.getLogger(__name__)

# Lazy singleton
_registry_instance: Optional[Any] = None


def get_api_registry():
    """Get or initialize the Cloud API Registry client."""
    global _registry_instance

    if _registry_instance is not None:
        return _registry_instance

    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        logger.warning("PROJECT_ID not set - ApiRegistry disabled")
        return None

    try:
        from google.adk.tools import ApiRegistry

        # Optional: header provider for auth propagation
        header_provider = _get_header_provider()

        _registry_instance = ApiRegistry(
            project_id=project_id,
            header_provider=header_provider
        )
        logger.info(f"✅ Initialized ApiRegistry for project: {project_id}")
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
```

### Phase 2: Registry-Backed Tool Fetching

Add functions to fetch tools from the registry:

```python
# agents/shared_tools/api_registry.py (continued)

def get_registry_tools(
    mcp_server_name: str,
    tool_filter: Optional[list[str]] = None
) -> list[Any]:
    """
    Fetch tools from a registered MCP server.

    Args:
        mcp_server_name: Full resource name of the MCP server
            e.g., "projects/{project}/locations/global/mcpServers/{server-id}"
        tool_filter: Optional list of specific tool names to fetch

    Returns:
        List of tools from the registry, or empty list on failure
    """
    registry = get_api_registry()
    if registry is None:
        logger.warning("ApiRegistry not available - returning empty tools")
        return []

    try:
        toolset = registry.get_toolset(
            mcp_server_name=mcp_server_name,
            tool_filter=tool_filter
        )
        logger.info(f"✅ Fetched {len(toolset)} tools from {mcp_server_name}")
        return [toolset]
    except Exception as e:
        logger.error(f"Failed to fetch tools from {mcp_server_name}: {e}")
        return []


# Pre-defined MCP server resource names for Bob's Brain
MCP_SERVERS = {
    "bigquery": "projects/{project}/locations/global/mcpServers/google-bigquery.googleapis.com-mcp",
    "github": "projects/{project}/locations/global/mcpServers/github.com-mcp",
    "filesystem": "projects/{project}/locations/global/mcpServers/filesystem-mcp",
}


def get_bigquery_registry_tools(filter_tools: Optional[list[str]] = None) -> list[Any]:
    """Get BigQuery tools from API Registry."""
    project_id = os.getenv("PROJECT_ID", "")
    server_name = MCP_SERVERS["bigquery"].format(project=project_id)

    # Default filter for common BQ operations
    if filter_tools is None:
        filter_tools = ["list_dataset_ids", "execute_sql", "get_table_schema"]

    return get_registry_tools(server_name, filter_tools)
```

### Phase 3: Hybrid Tool Profiles

Update agent tool profiles to use both static and registry tools:

```python
# agents/shared_tools/__init__.py (updated)

from .api_registry import get_api_registry, get_bigquery_registry_tools


def get_bob_tools() -> List[Any]:
    """Bob's tool profile - hybrid static + registry."""
    tools = []

    # Static tools (always available)
    tools.append(get_google_search_tool())
    tools.extend(get_adk_docs_tools())

    # Vertex Search (if configured)
    vertex_tool = get_bob_vertex_search_tool()
    if vertex_tool:
        tools.append(vertex_tool)

    # Registry tools (dynamic, if available)
    registry = get_api_registry()
    if registry:
        # Add registry-managed tools
        registry_tools = get_bigquery_registry_tools()
        tools.extend(registry_tools)
        logger.info(f"Added {len(registry_tools)} registry tools for Bob")

    logger.info(f"Loaded {len(tools)} total tools for Bob")
    return tools
```

---

## MCP Server Candidates

Based on current tool analysis, these are candidates for MCP server migration:

| Tool Category | Current Location | MCP Server Candidate | Priority |
|--------------|------------------|---------------------|----------|
| Repository ops | `custom_tools.py` | `mcp-repo-ops` | High |
| GitHub API | `custom_tools.py` | `mcp-github` | High |
| ADK analyzer | `custom_tools.py` | `mcp-adk-analyzer` | Medium |
| BigQuery | `adk_builtin.py` | Google's BQ MCP | Low (already built-in) |

### mcp-repo-ops

Repository operations that could become an MCP server:
- `search_codebase` - Semantic code search
- `get_file_contents` - File retrieval
- `analyze_dependencies` - Dependency graph
- `check_patterns` - Pattern compliance

### mcp-github

GitHub operations:
- `create_issue` - Issue creation
- `create_pr` - Pull request management
- `list_workflows` - CI/CD status
- `get_reviews` - Code review status

---

## Hard Mode Compliance

### R1: ADK-Only
- ✅ Uses `google.adk.tools.ApiRegistry` (ADK native)
- ✅ No external frameworks

### R3: Gateway Separation
- ✅ Registry calls go through Cloud Run gateway (same as other API calls)
- ✅ No direct Agent Engine access

### R4: CI-Only Changes
- ✅ MCP server registration happens via Terraform/CI
- ✅ Agents only discover, not modify

### R5: Dual Memory
- ✅ Tool list can be stored in session for consistency
- ✅ No impact on memory wiring

### R7: SPIFFE ID
- ✅ Header provider propagates auth context
- ✅ Registry respects IAM permissions

---

## Implementation Phases

### Phase 1: Foundation (1-2 weeks)
- [ ] Create `agents/shared_tools/api_registry.py`
- [ ] Add `get_api_registry()` singleton
- [ ] Add header provider for R7 compliance
- [ ] Unit tests (no external calls)
- [ ] Update this doc with implementation status

### Phase 2: First MCP Server (2-3 weeks)
- [ ] Register BigQuery MCP in Cloud Console
- [ ] Add `get_bigquery_registry_tools()`
- [ ] Integration test with real registry
- [ ] Document MCP server setup in 000-docs/

### Phase 3: Custom MCP Servers (4-6 weeks)
- [ ] Design `mcp-repo-ops` server
- [ ] Deploy to Cloud Run
- [ ] Register in API Registry
- [ ] Migrate tools from `custom_tools.py`

### Phase 4: Full Migration (ongoing)
- [ ] Migrate remaining tool categories
- [ ] Deprecate static tool definitions
- [ ] Add registry health checks to ARV

---

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_api_registry.py

def test_registry_not_available_returns_none():
    """Without PROJECT_ID, registry should return None gracefully."""
    with patch.dict(os.environ, {}, clear=True):
        registry = get_api_registry()
        assert registry is None

def test_registry_tools_empty_on_failure():
    """On registry failure, should return empty list (not crash)."""
    tools = get_registry_tools("invalid/server/name")
    assert tools == []
```

### Integration Tests
```python
# tests/integration/test_api_registry_live.py

@pytest.mark.skipif(not os.getenv("PROJECT_ID"), reason="No project configured")
def test_registry_initializes():
    """Registry should initialize with valid project."""
    registry = get_api_registry()
    assert registry is not None
```

---

## References

- [Cloud API Registry Announcement](https://cloud.google.com/vertex-ai/docs/agent-builder/api-registry) (when public)
- [ADK Tools Documentation](https://google.github.io/adk-docs/tools/)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- Bob's Brain Hard Mode Rules: `000-docs/6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-20 | Proposed hybrid approach | Keeps existing tools working while adding registry capability |
| 2025-12-20 | Start with BigQuery MCP | Google provides it, lowest risk first integration |
| 2025-12-20 | Lazy singleton for registry | Matches existing ADK App pattern (6767-LAZY standard) |
