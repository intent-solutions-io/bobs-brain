"""
Foreman Agent - Orchestrator for IAM Department

TODO: Rename this package to match your orchestrator agent name.

This agent follows the ADK lazy-loading pattern (6767-LAZY) and
serves as the central coordinator for specialist agents.

Reference Implementation:
- bobs-brain/agents/iam_senior_adk_devops_lead/

Hard Mode Rules:
- R1: ADK-only (no LangChain, CrewAI)
- R5: Dual memory wiring (Session + MemoryBank)
"""

# Lazy-loading pattern: don't import agent at module level
# Use get_agent() or access via agent.py::app

__version__ = "0.1.0"
