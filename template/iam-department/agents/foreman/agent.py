"""
Foreman Agent - Main Agent Definition

This file defines the orchestrator agent using ADK lazy-loading pattern.

TODO:
1. Replace FOREMAN_PROMPT with your agent's system prompt
2. Define skills/tools appropriate for your orchestrator
3. Configure after_agent_callback for R5 memory wiring

Reference: bobs-brain/agents/iam_senior_adk_devops_lead/agent.py
"""

from typing import Any, Callable, Dict, Optional

# ADK imports (R1 compliance)
try:
    from google.adk import Agent
    from google.adk.agents import LlmAgent
    from google.adk.tools import Tool
except ImportError:
    # Fallback for environments without ADK
    Agent = None
    LlmAgent = None
    Tool = None


# System prompt - TODO: Customize for your use case
FOREMAN_PROMPT = """
You are a Foreman agent - the orchestrator for an IAM (Intent Agent Model) department.

Your responsibilities:
1. Receive tasks from the user or upstream agent
2. Plan and delegate work to specialist agents
3. Coordinate multi-step workflows
4. Aggregate results and return to caller

You follow the A2A protocol for agent-to-agent communication.

Specialists available:
- [TODO: List your specialist agents here]

Current environment: {{ENVIRONMENT}}
SPIFFE ID: {{SPIFFE_ID}}
"""


def get_agent() -> Optional[Any]:
    """
    Lazy-load and return the Foreman agent.

    This function is called by the Agent Engine to get the agent instance.
    Using lazy loading avoids importing heavy dependencies at module load time.

    Returns:
        LlmAgent instance or None if ADK not available
    """
    if LlmAgent is None:
        print("Warning: ADK not installed. Agent not available.")
        return None

    # Define agent tools
    tools = [
        # TODO: Add your tools here
        # Example:
        # Tool(
        #     name="delegate_to_specialist",
        #     description="Delegate a task to a specialist agent",
        #     func=delegate_to_specialist,
        # ),
    ]

    # Create agent
    agent = LlmAgent(
        name="foreman",
        model="gemini-2.0-flash-exp",
        system_instruction=FOREMAN_PROMPT,
        tools=tools,
    )

    return agent


# Module-level app for Agent Engine deployment
# This is the entrypoint for inline source deployment
app = None


def _initialize_app():
    """Initialize the app lazily."""
    global app
    if app is None:
        try:
            from vertexai import agent_engines
            agent = get_agent()
            if agent:
                app = agent_engines.AdkApp(
                    agent=agent,
                    enable_tracing=True,
                )
        except ImportError:
            pass


# Don't initialize at import time - lazy loading pattern
# Agent Engine will call get_agent() or access app when needed


# Callback for R5 memory wiring (optional)
def after_agent_callback(
    agent: Any,
    response: Any,
    context: Dict[str, Any],
) -> None:
    """
    After-agent callback for memory wiring.

    This callback is invoked after each agent response for R5 compliance:
    - Store conversation turn in VertexAiSessionService
    - Update VertexAiMemoryBankService if configured

    TODO: Implement memory wiring based on your requirements.
    """
    pass
