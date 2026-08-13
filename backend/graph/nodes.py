import os
import logging
from typing import Dict, Any, List, Optional
import pandas as pd

from backend.schemas.enums import JobStatus, DecisionType
from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief, MissionConstraints
from backend.schemas.experiment import ExperimentPlan, ExperimentResult
from backend.schemas.evaluation import EvaluationReport, ResearchDirectorDecision
from backend.schemas.report import FinalRecommendation

from backend.profiling import ProfilingEngine
from backend.ml_execution.executor import MLExecutionEngine
from backend.evaluation.evaluator import EvaluationEngine

from backend.agents import (
    DatasetUnderstandingAgent,
    ConstraintGoalAnalyzer,
    StrategyPlannerAgent,
    ResearchDirectorAgent,
    ReportGeneratorAgent,
)
from backend.graph.state import WorkflowStateDict

logger = logging.getLogger("datapilot.graph.nodes")


def profiling_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Executes Phase 6 ProfilingEngine on dataset file."""
    file_path = state.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Dataset file not found at path: {file_path}",
        }

    try:
        profile, hints = ProfilingEngine.profile_file(file_path)
        return {
            **state,
            "semantic_profile": profile.model_dump(),
            "job_status": JobStatus.PROFILING.value,
        }
    except Exception as e:
        logger.error(f"Profiling failed: {str(e)}", exc_info=True)
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Profiling failed: {str(e)}",
        }


def understanding_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 7 DatasetUnderstandingAgent to build MissionBrief."""
    if state.get("job_status") == JobStatus.FAILED.value:
        return state

    try:
        profile_dict = dict(state.get("semantic_profile") or {})
        err = profile_dict.pop("error", None)
        if err:
            logger.warning(f"SemanticProfile fallback error encountered: {err}")
        profile = SemanticProfile(**profile_dict)
        user_goal = state.get("user_goal") or "Optimize machine learning model performance"

        agent = DatasetUnderstandingAgent()
        mission_brief = agent.run({
            "semantic_profile": profile,
            "user_goal": user_goal,
        })

        return {
            **state,
            "mission_brief": mission_brief.model_dump(),
            "job_status": JobStatus.PLANNING.value,
        }
    except Exception as e:
        logger.error(f"Dataset Understanding Agent failed: {str(e)}", exc_info=True)
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Dataset Understanding Agent failed: {str(e)}",
        }


def planning_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 7 StrategyPlannerAgent to generate candidate ExperimentPlan."""
    if state.get("job_status") == JobStatus.FAILED.value:
        return state

    iteration = state.get("iteration_count", 0) + 1

    try:
        profile_dict = dict(state.get("semantic_profile") or {})
        err = profile_dict.pop("error", None)
        if err:
            logger.warning(f"SemanticProfile fallback error encountered: {err}")
        mission_dict = state.get("mission_brief") or {}

        profile = SemanticProfile(**profile_dict)
        mission = MissionBrief(**mission_dict)

        dataset_summary = profile_dict.get("dataset_summary", {})
        target_info = dataset_summary.get("target", {})
        task_type = target_info.get("task_type") or "classification"

        planner = StrategyPlannerAgent()
        plan = planner.run({
            "semantic_profile": profile,
            "mission_brief": mission,
            "experiment_budget": 2,
            "task_type": task_type,
        })

        return {
            **state,
            "iteration_count": iteration,
            "experiment_plan": plan.model_dump(),
            "job_status": JobStatus.EXECUTING.value,
        }
    except Exception as e:
        logger.error(f"Strategy Planner failed: {str(e)}", exc_info=True)
        return {
            **state,
            "iteration_count": iteration,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Strategy Planner failed: {str(e)}",
        }


def execution_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Executes proposed experiments using Phase 4 ML Execution Engine."""
    if state.get("job_status") == JobStatus.FAILED.value:
        return state

    plan_dict = state.get("experiment_plan")
    file_path = state.get("file_path")
    profile_dict = state.get("semantic_profile") or {}
    dataset_summary = profile_dict.get("dataset_summary", {})
    target_info = dataset_summary.get("target", {})
    target_col = target_info.get("target_column") or "target"
    task_type = target_info.get("task_type") or "classification"

    if not plan_dict or not file_path or not os.path.exists(file_path):
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": "Execution failed: Missing experiment plan or dataset file.",
        }

    try:
        df = pd.read_csv(file_path)
        plan = ExperimentPlan(**plan_dict)

        ml_engine = MLExecutionEngine(max_workers=2)
        batch_results = ml_engine.execute_plan(
            plan=plan,
            dataset=df,
            target_column=target_col,
            task_type=task_type,
        )

        existing_results = list(state.get("experiment_results") or [])
        existing_results.extend([r.model_dump() for r in batch_results])
        return {
            **state,
            "experiment_results": existing_results,
            "job_status": JobStatus.EVALUATING.value,
        }

    except Exception as e:
        logger.error(f"Execution failed: {str(e)}", exc_info=True)
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Execution failed: {str(e)}",
        }


def evaluation_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Evaluates batch results using Phase 5 EvaluationEngine."""
    if state.get("job_status") == JobStatus.FAILED.value:
        return state

    results_dicts = state.get("experiment_results") or []
    if not results_dicts:
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": "Evaluation failed: No experiment results found.",
        }

    try:
        results = [ExperimentResult(**r) for r in results_dicts]
        eval_engine = EvaluationEngine()
        eval_report, dec = eval_engine.evaluate_batch(
            results=results,
            job_id=state.get("job_id", "job_default"),
        )

        existing_kb = list(state.get("knowledge_base") or [])
        for f in eval_report.knowledge:
            existing_kb.append(f.model_dump())

        return {
            **state,
            "evaluation_report": eval_report.model_dump(),
            "knowledge_base": existing_kb,
        }

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Evaluation failed: {str(e)}",
        }


def decision_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 7 ResearchDirectorAgent and budget manager to set decision."""
    if state.get("job_status") == JobStatus.FAILED.value:
        return state

    iteration = state.get("iteration_count", 1)
    max_iter = state.get("max_iterations", 5)

    eval_report_dict = state.get("evaluation_report")
    if not eval_report_dict:
        stop_decision = ResearchDirectorDecision(
            decision=DecisionType.STOP,
            confidence=1.0,
            knowledge=["No evaluation report available."],
        )
        return {
            **state,
            "decision": stop_decision.model_dump(),
        }

    try:
        eval_report = EvaluationReport(**eval_report_dict)
        director = ResearchDirectorAgent()
        decision = director.run({"evaluation_report": eval_report})

        # Override decision if budget limit reached
        if iteration >= max_iter:
            decision = ResearchDirectorDecision(
                decision=DecisionType.STOP,
                confidence=0.95,
                knowledge=decision.knowledge + [f"Budget limit reached ({max_iter} iterations)."],
            )

        return {
            **state,
            "decision": decision.model_dump(),
        }
    except Exception as e:
        logger.error(f"Research Director Agent failed: {str(e)}", exc_info=True)
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Research Director Agent failed: {str(e)}",
        }


def reporting_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 7 ReportGeneratorAgent to create final recommendation."""
    if state.get("job_status") == JobStatus.FAILED.value:
        return state

    eval_report_dict = state.get("evaluation_report")
    if not eval_report_dict:
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": "Reporting failed: Missing evaluation report.",
        }

    try:
        eval_report = EvaluationReport(**eval_report_dict)
        reporter = ReportGeneratorAgent()
        final_rec = reporter.run({"evaluation_report": eval_report})

        return {
            **state,
            "final_report": final_rec.model_dump(),
            "job_status": JobStatus.COMPLETED.value,
        }
    except Exception as e:
        logger.error(f"Report Generator Agent failed: {str(e)}", exc_info=True)
        return {
            **state,
            "job_status": JobStatus.FAILED.value,
            "error_message": f"Report Generator Agent failed: {str(e)}",
        }
