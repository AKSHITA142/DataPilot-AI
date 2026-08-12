import os
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


import logging
from backend.core.logging_config import log_phase_banner

logger = logging.getLogger("datapilot.graph.nodes")


def profiling_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Executes Phase 6 ProfilingEngine on dataset file."""
    file_path = state.get("file_path")
    logger.info(f"[GRAPH NODE: PROFILING] Executing Profiling Node for file: {file_path}")
    if not file_path or not os.path.exists(file_path):
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Dataset file not found at path: {file_path}"
        logger.error(f"[GRAPH NODE: PROFILING FAILED] File not found: {file_path}")
        return state

    try:
        profile, hints = ProfilingEngine.profile_file(file_path)
        state["semantic_profile"] = profile.model_dump()
        state["job_status"] = JobStatus.PROFILING.value
        logger.info(f"[GRAPH NODE: PROFILING SUCCESS] Profile generated. Rows: {profile.dataset_summary.get('rows')}, Cols: {profile.dataset_summary.get('columns')}")
    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Profiling failed: {str(e)}"
        logger.error(f"[GRAPH NODE: PROFILING ERROR] Exception: {e}", exc_info=True)

    return state


def understanding_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 5 DatasetUnderstandingAgent to build MissionBrief."""
    if state.get("job_status") == JobStatus.FAILED.value:
        logger.warning("[GRAPH NODE: UNDERSTANDING SKIPPED] Job in FAILED state.")
        return state

    log_phase_banner("Phase 05: Dataset Understanding Agent", "Translating SemanticProfile into MissionBrief")
    try:
        profile_dict = state.get("semantic_profile") or {}
        profile = SemanticProfile(**profile_dict)
        user_goal = state.get("user_goal") or "Optimize machine learning model performance"
        logger.info(f"[GRAPH NODE: UNDERSTANDING] Processing User Goal: '{user_goal}'")

        agent = DatasetUnderstandingAgent()
        mission_brief = agent.run({
            "semantic_profile": profile,
            "user_goal": user_goal,
        })

        state["mission_brief"] = mission_brief.model_dump()
        state["job_status"] = JobStatus.PLANNING.value
        logger.info(f"[GRAPH NODE: UNDERSTANDING SUCCESS] MissionBrief objective: '{mission_brief.objective}' | Target Metric: {mission_brief.success_metrics}")
    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Dataset Understanding Agent failed: {str(e)}"
        logger.error(f"[GRAPH NODE: UNDERSTANDING ERROR] Exception: {e}", exc_info=True)

    return state


def planning_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 5 StrategyPlannerAgent to generate candidate ExperimentPlan."""
    if state.get("job_status") == JobStatus.FAILED.value:
        logger.warning("[GRAPH NODE: PLANNING SKIPPED] Job in FAILED state.")
        return state

    iteration = state.get("iteration_count", 0) + 1
    state["iteration_count"] = iteration

    log_phase_banner(f"Phase 05 & 07: Experiment Planning (Iteration {iteration})", "Generating prioritized ML experiment candidates")
    try:
        profile_dict = state.get("semantic_profile") or {}
        mission_dict = state.get("mission_brief") or {}

        profile = SemanticProfile(**profile_dict)
        mission = MissionBrief(**mission_dict)

        dataset_summary = profile_dict.get("dataset_summary", {})
        target_info = dataset_summary.get("target", {})
        task_type = target_info.get("task_type") or "classification"

        logger.info(f"[GRAPH NODE: PLANNING] Task Type: '{task_type}' | Iteration: {iteration}/5")
        planner = StrategyPlannerAgent()
        plan = planner.run({
            "semantic_profile": profile,
            "mission_brief": mission,
            "experiment_budget": 2,
            "task_type": task_type,
        })

        state["experiment_plan"] = plan.model_dump()
        state["job_status"] = JobStatus.EXECUTING.value
        logger.info(f"[GRAPH NODE: PLANNING SUCCESS] Generated plan with {len(plan.experiments)} candidate experiments: {[e.model_name for e in plan.experiments]}")
    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Strategy Planner failed: {str(e)}"
        logger.error(f"[GRAPH NODE: PLANNING ERROR] Exception: {e}", exc_info=True)

    return state


def execution_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Executes proposed experiments using Phase 4 ML Execution Engine."""
    if state.get("job_status") == JobStatus.FAILED.value:
        logger.warning("[GRAPH NODE: EXECUTION SKIPPED] Job in FAILED state.")
        return state

    log_phase_banner("Phase 04: ML Execution Engine", "Training ML pipelines & running cross-validation")
    plan_dict = state.get("experiment_plan")
    file_path = state.get("file_path")
    profile_dict = state.get("semantic_profile") or {}
    dataset_summary = profile_dict.get("dataset_summary", {})
    target_info = dataset_summary.get("target", {})
    target_col = target_info.get("target_column") or "target"
    task_type = target_info.get("task_type") or "classification"

    if not plan_dict or not file_path or not os.path.exists(file_path):
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = "Execution failed: Missing experiment plan or dataset file."
        logger.error(f"[GRAPH NODE: EXECUTION FAILED] Plan present: {bool(plan_dict)}, File present: {os.path.exists(file_path) if file_path else False}")
        return state

    try:
        df = pd.read_csv(file_path)
        plan = ExperimentPlan(**plan_dict)

        logger.info(f"[GRAPH NODE: EXECUTION] Executing {len(plan.experiments)} experiments on target '{target_col}' ({task_type})")
        ml_engine = MLExecutionEngine(max_workers=2)
        batch_results = ml_engine.execute_plan(
            plan=plan,
            dataset=df,
            target_column=target_col,
            task_type=task_type,
        )

        existing_results = state.get("experiment_results") or []
        existing_results.extend([r.model_dump() for r in batch_results])
        state["experiment_results"] = existing_results
        state["job_status"] = JobStatus.EVALUATING.value
        logger.info(f"[GRAPH NODE: EXECUTION SUCCESS] Executed {len(batch_results)} pipelines. Total results in memory: {len(existing_results)}")

    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Execution failed: {str(e)}"
        logger.error(f"[GRAPH NODE: EXECUTION ERROR] Exception: {e}", exc_info=True)

    return state


def evaluation_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Evaluates batch results using Phase 8 EvaluationEngine."""
    if state.get("job_status") == JobStatus.FAILED.value:
        logger.warning("[GRAPH NODE: EVALUATION SKIPPED] Job in FAILED state.")
        return state

    log_phase_banner("Phase 08: Multi-Objective Evaluation & Ranking", "Scoring 5D composite metrics & distilling knowledge")
    results_dicts = state.get("experiment_results") or []
    if not results_dicts:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = "Evaluation failed: No experiment results found."
        logger.error("[GRAPH NODE: EVALUATION FAILED] No experiment results in state.")
        return state

    try:
        results = [ExperimentResult(**r) for r in results_dicts]
        eval_engine = EvaluationEngine()
        eval_report, dec = eval_engine.evaluate_batch(
            results=results,
            job_id=state.get("job_id", "job_default"),
        )

        state["evaluation_report"] = eval_report.model_dump()

        existing_kb = state.get("knowledge_base") or []
        for f in eval_report.knowledge:
            existing_kb.append(f.model_dump())
        state["knowledge_base"] = existing_kb

        top_exp = eval_report.ranking[0] if eval_report.ranking else None
        logger.info(f"[GRAPH NODE: EVALUATION SUCCESS] Top model: '{top_exp.model if top_exp else 'N/A'}' (Score: {top_exp.score if top_exp else 0:.4f}) | Knowledge items: {len(eval_report.knowledge)}")

    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Evaluation failed: {str(e)}"
        logger.error(f"[GRAPH NODE: EVALUATION ERROR] Exception: {e}", exc_info=True)

    return state


def decision_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 7 ResearchDirectorAgent and budget manager to set decision."""
    if state.get("job_status") == JobStatus.FAILED.value:
        logger.warning("[GRAPH NODE: DECISION SKIPPED] Job in FAILED state.")
        return state

    iteration = state.get("iteration_count", 1)
    max_iter = state.get("max_iterations", 5)

    log_phase_banner(f"Phase 07: Research Director Decision (Iteration {iteration}/{max_iter})", "Evaluating convergence gain & remaining iteration budget")
    eval_report_dict = state.get("evaluation_report")
    if not eval_report_dict:
        state["decision"] = ResearchDirectorDecision(
            decision=DecisionType.STOP,
            confidence=1.0,
            knowledge=["No evaluation report available."],
        ).model_dump()
        logger.warning("[GRAPH NODE: DECISION] No evaluation report found. Defaulting decision to STOP.")
        return state

    try:
        eval_report = EvaluationReport(**eval_report_dict)
        director = ResearchDirectorAgent()
        decision = director.run({"evaluation_report": eval_report})

        # Override decision if budget limit reached
        if iteration >= max_iter:
            logger.info(f"[GRAPH NODE: DECISION] Max iteration budget reached ({iteration}/{max_iter}). Enforcing STOP decision.")
            decision = ResearchDirectorDecision(
                decision=DecisionType.STOP,
                confidence=0.95,
                knowledge=decision.knowledge + [f"Budget limit reached ({max_iter} iterations)."],
            )

        state["decision"] = decision.model_dump()
        dec_val = getattr(decision.decision, "value", str(decision.decision))
        logger.info(f"[GRAPH NODE: DECISION SUCCESS] Director decision: {str(dec_val).upper()} (Confidence: {decision.confidence:.2f})")
    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Research Director Agent failed: {str(e)}"
        logger.error(f"[GRAPH NODE: DECISION ERROR] Exception: {e}", exc_info=True)

    return state


def reporting_node(state: WorkflowStateDict) -> WorkflowStateDict:
    """Invokes Phase 10 ReportGeneratorAgent to create final recommendation."""
    if state.get("job_status") == JobStatus.FAILED.value:
        logger.warning("[GRAPH NODE: REPORTING SKIPPED] Job in FAILED state.")
        return state

    log_phase_banner("Phase 10: Final Recommendation Synthesis", "Compiling Markdown research report & glassmorphism web payload")
    eval_report_dict = state.get("evaluation_report")
    if not eval_report_dict:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = "Reporting failed: Missing evaluation report."
        logger.error("[GRAPH NODE: REPORTING FAILED] Missing evaluation report.")
        return state

    try:
        eval_report = EvaluationReport(**eval_report_dict)
        reporter = ReportGeneratorAgent()
        final_rec = reporter.run({"evaluation_report": eval_report})

        state["final_report"] = final_rec.model_dump()
        state["job_status"] = JobStatus.COMPLETED.value
        logger.info(f"[GRAPH NODE: REPORTING SUCCESS] Final recommendation compiled for Winning Experiment: {final_rec.winning_experiment_id} ({final_rec.model})")
    except Exception as e:
        state["job_status"] = JobStatus.FAILED.value
        state["error_message"] = f"Report Generator Agent failed: {str(e)}"
        logger.error(f"[GRAPH NODE: REPORTING ERROR] Exception: {e}", exc_info=True)

    return state
