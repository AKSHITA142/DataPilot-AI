from typing import Literal
from backend.schemas.enums import DecisionType, JobStatus
from backend.graph.state import WorkflowStateDict


def route_next(state: WorkflowStateDict) -> Literal["planning", "reporting", "__end__"]:
    """
    Conditional routing function for LangGraph.
    Evaluates ResearchDirectorDecision and iteration budget.
    """
    # 1. Terminal/Error state check
    if state.get("job_status") == JobStatus.FAILED.value:
        return "__end__"

    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 5)

    # 2. Budget limit check
    if iteration >= max_iterations:
        return "reporting"

    # 3. Decision check
    decision_dict = state.get("decision") or {}
    dec_val = decision_dict.get("decision")

    if dec_val in [DecisionType.STOP.value, "STOP", "finish"]:
        return "reporting"

    if dec_val in [
        DecisionType.CONTINUE.value, "CONTINUE",
        DecisionType.EXPLORE.value, "EXPLORE",
        DecisionType.REFINE.value, "REFINE"
    ]:
        return "planning"

    # Default fallback: route to reporting if decision missing
    return "reporting"
