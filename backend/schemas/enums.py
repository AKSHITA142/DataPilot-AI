from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROFILING = "profiling"
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    DIRECTING = "directing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DecisionType(str, Enum):
    STOP = "stop"
    CONTINUE = "continue"
    EXPLORE = "explore"
    REFINE = "refine"


class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ColumnType(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"
