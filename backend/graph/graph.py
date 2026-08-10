from langgraph.graph import StateGraph, START, END
from backend.graph.state import WorkflowStateDict
from backend.graph.nodes import (
    profiling_node,
    understanding_node,
    planning_node,
    execution_node,
    evaluation_node,
    decision_node,
    reporting_node,
)
from backend.graph.router import route_next
from backend.graph.checkpoint import get_checkpointer


def build_research_graph() -> StateGraph:
    """Builds uncompiled StateGraph for DataPilot-AI research workflow."""
    workflow = StateGraph(WorkflowStateDict)

    # Add Nodes
    workflow.add_node("profiling", profiling_node)
    workflow.add_node("understanding", understanding_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("evaluation", evaluation_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("reporting", reporting_node)

    # Wire Edges
    workflow.add_edge(START, "profiling")
    workflow.add_edge("profiling", "understanding")
    workflow.add_edge("understanding", "planning")
    workflow.add_edge("planning", "execution")
    workflow.add_edge("execution", "evaluation")
    workflow.add_edge("evaluation", "decision")

    # Conditional Routing Edge from decision node
    workflow.add_conditional_edges(
        "decision",
        route_next,
        {
            "planning": "planning",
            "reporting": "reporting",
            "__end__": END,
        }
    )

    workflow.add_edge("reporting", END)
    return workflow


def compile_graph(checkpointer=None):
    """Compiles research graph with checkpointer enabled."""
    checkpointer = checkpointer or get_checkpointer()
    graph_builder = build_research_graph()
    return graph_builder.compile(checkpointer=checkpointer)
