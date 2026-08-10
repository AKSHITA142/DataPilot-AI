/**
 * Canonical Data Contracts & Shared Types for DataPilot-AI
 * Mirrors Pydantic models in backend/schemas/
 */

export type JobStatus =
  | 'queued'
  | 'profiling'
  | 'understanding'
  | 'planning'
  | 'executing'
  | 'evaluating'
  | 'directing'
  | 'reporting'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type DecisionType = 'stop' | 'continue' | 'explore' | 'refine';

export type TaskType = 'classification' | 'regression';

export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

export type ColumnType =
  | 'numeric'
  | 'categorical'
  | 'datetime'
  | 'text'
  | 'boolean'
  | 'unknown';

export interface ConfidenceScoredModel {
  confidence: number;
}

export interface ColumnProfile {
  name: string;
  type: ColumnType;
  missing_count: number;
  missing_pct: number;
  distinct_count: number;
  skewness?: number | null;
  mean?: number | null;
  std?: number | null;
  min?: number | null;
  max?: number | null;
  sample_values: any[];
}

export interface QualityIssue extends ConfidenceScoredModel {
  problem: string;
  severity: SeverityLevel;
  description?: string | null;
  affected_columns: string[];
}

export interface ResourceProfile {
  execution_mode: string;
  use_lazy_loading: boolean;
  recommended_workers: number;
  memory_mb: number;
}

export interface SemanticProfile {
  dataset_summary: Record<string, any>;
  column_profiles: ColumnProfile[];
  quality_issues: QualityIssue[];
  resource_profile?: ResourceProfile | null;
  recommendation_context: Record<string, any>;
}

export interface MissionConstraints {
  max_row_loss: number;
  use_only_open_source_models: boolean;
  training_time_limit_minutes: number;
  forbidden_operations: string[];
  custom_constraints: Record<string, any>;
}

export interface DatasetCharacteristics {
  domain: string;
  risk_level: string;
  complexity: string;
}

export interface MissionBrief {
  objective: string;
  constraints: MissionConstraints;
  dataset_characteristics: DatasetCharacteristics;
  success_metrics: string[];
  avoid: string[];
}

export interface ExperimentOperation {
  type: string;
  method: string;
  params: Record<string, any>;
}

export interface ExperimentSpec {
  experiment_id: string;
  priority: number;
  reason: string;
  operations: ExperimentOperation[];
  model_name: string;
}

export interface ExperimentPlan {
  mission: string;
  experiment_budget: number;
  experiments: ExperimentSpec[];
}

export interface PipelineDefinition {
  operations: ExperimentOperation[];
  model_name: string;
}

export interface MetricsResult {
  primary_metric: number;
  metrics: Record<string, number>;
  cv_scores: number[];
}

export interface Artifacts {
  model_path?: string | null;
  feature_importance?: Record<string, number> | null;
  confusion_matrix?: number[][] | null;
  plots: Record<string, string>;
}

export interface ExperimentResult {
  experiment_id: string;
  pipeline: PipelineDefinition;
  model: string;
  metrics: MetricsResult;
  runtime: number;
  status: string;
  artifacts?: Artifacts | null;
  error_message?: string | null;
}

export interface RankingItem {
  rank: number;
  experiment_id: string;
  score: number;
  model: string;
}

export interface KnowledgeFinding extends ConfidenceScoredModel {
  finding: string;
  evidence: Record<string, any>;
}

export interface EvaluationReport {
  winner: string;
  ranking: RankingItem[];
  knowledge: KnowledgeFinding[];
  should_continue: boolean;
  reason: string;
}

export interface ResearchDirectorDecision extends ConfidenceScoredModel {
  decision: DecisionType;
  knowledge: string[];
  remaining_questions: string[];
  next_experiments: ExperimentSpec[];
}

export interface FinalRecommendation {
  winning_experiment_id: string;
  pipeline: PipelineDefinition;
  model: string;
  final_metrics: Record<string, number>;
  summary: string;
  key_findings: string[];
  exported_artifacts: Record<string, string>;
}

export interface WorkflowState {
  dataset_id: string;
  job_status: JobStatus;
  user_goal?: string | null;
  semantic_profile?: SemanticProfile | null;
  mission_brief?: MissionBrief | null;
  experiment_plan?: ExperimentPlan | null;
  experiment_results: ExperimentResult[];
  evaluation_report?: EvaluationReport | null;
  knowledge_base: KnowledgeFinding[];
  decision?: ResearchDirectorDecision | null;
  final_report?: FinalRecommendation | null;
  error_message?: string | null;
}

export interface SuccessResponse<T = any> {
  data: T;
  meta: Record<string, any>;
}

export interface ErrorResponse {
  error_code: string;
  message: string;
  details: Record<string, any>;
}
