"""
Workflow Agents Module - Multi-Agent Orchestration Patterns

This module implements Google's recommended multi-agent patterns using ADK primitives:
- SequentialAgent for pipeline workflows
- ParallelAgent for concurrent execution (Phase 2)
- LoopAgent for iterative refinement (Phase 3)

Reference: https://developers.googleblog.com/en/developers-guide-to-multi-agent-patterns-in-adk/

Phase 1: Sequential Workflow Foundation
- compliance_workflow.py: iam-adk -> iam-issue -> iam-fix-plan

Phase 2: Parallel Execution
- analysis_workflow.py: ParallelAgent(iam-adk, iam-cleanup, iam-index) -> aggregator

Phase 3: Quality Gates (Generator-Critic + LoopAgent)
- fix_loop.py: LoopAgent(iam-fix-impl -> iam-qa) with max_iterations=3
"""

from agents.workflows.compliance_workflow import (
    create_compliance_workflow,
    create_analysis_agent,
    create_issue_agent,
    create_planning_agent,
)

from agents.workflows.analysis_workflow import (
    create_parallel_analysis,
    create_result_aggregator,
    create_analysis_workflow,
)

from agents.workflows.fix_loop import (
    create_fix_review,
    create_fix_loop,
    create_qa_escalation_callback,
)

__all__ = [
    # Phase 1: Sequential Workflow
    "create_compliance_workflow",
    "create_analysis_agent",
    "create_issue_agent",
    "create_planning_agent",
    # Phase 2: Parallel Execution
    "create_parallel_analysis",
    "create_result_aggregator",
    "create_analysis_workflow",
    # Phase 3: Quality Gates (LoopAgent)
    "create_fix_review",
    "create_fix_loop",
    "create_qa_escalation_callback",
]
