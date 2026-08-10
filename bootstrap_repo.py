import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

# Backend package directories
BACKEND_DIRS = [
    "backend",
    "backend/api",
    "backend/api/routes",
    "backend/api/schemas",
    "backend/api/dependencies",
    "backend/core",
    "backend/services",
    "backend/repositories",
    "backend/middleware",
    "backend/models",
    "backend/schemas",
    "backend/workers",
    "backend/graph",
    "backend/profiling",
    "backend/agents",
    "backend/agents/dataset_understanding",
    "backend/agents/strategy_planner",
    "backend/agents/research_director",
    "backend/ml_execution",
    "backend/evaluation",
    "backend/database",
    "backend/storage",
]

# Backend specific module files per folder-structure.md and backend-folder-structure.md
BACKEND_FILES = [
    # api/routes
    "backend/api/routes/upload.py",
    "backend/api/routes/jobs.py",
    "backend/api/routes/reports.py",
    "backend/api/routes/experiments.py",
    # core
    "backend/core/config.py",
    "backend/core/security.py",
    "backend/core/exceptions.py",
    # services
    "backend/services/dataset_service.py",
    "backend/services/job_service.py",
    "backend/services/report_service.py",
    "backend/services/experiment_service.py",
    # repositories
    "backend/repositories/dataset_repository.py",
    "backend/repositories/job_repository.py",
    "backend/repositories/experiment_repository.py",
    # middleware
    "backend/middleware/auth_middleware.py",
    "backend/middleware/logging_middleware.py",
    "backend/middleware/exception_middleware.py",
    # workers
    "backend/workers/research_worker.py",
    # graph (LangGraph orchestrator)
    "backend/graph/state.py",
    "backend/graph/nodes.py",
    "backend/graph/edges.py",
    "backend/graph/router.py",
    "backend/graph/graph.py",
    "backend/graph/checkpoint.py",
    # ml_execution (Execution Brain)
    "backend/ml_execution/validator.py",
    "backend/ml_execution/pipeline_builder.py",
    "backend/ml_execution/transformers.py",
    "backend/ml_execution/feature_engineering.py",
    "backend/ml_execution/trainer.py",
    "backend/ml_execution/cross_validation.py",
    "backend/ml_execution/metrics.py",
    "backend/ml_execution/logger.py",
    "backend/ml_execution/executor.py",
]

# Frontend directories per frontend-folder-structure.md
FRONTEND_DIRS = [
    "frontend",
    "frontend/src",
    "frontend/src/pages",
    "frontend/src/pages/LandingPage",
    "frontend/src/pages/DatasetUploadPage",
    "frontend/src/pages/DatasetIntelligencePage",
    "frontend/src/pages/ResearchTimelinePage",
    "frontend/src/pages/ExperimentExplorerPage",
    "frontend/src/pages/KnowledgeEvolutionPage",
    "frontend/src/pages/FinalRecommendationPage",
    "frontend/src/components",
    "frontend/src/components/buttons",
    "frontend/src/components/cards",
    "frontend/src/components/tables",
    "frontend/src/components/forms",
    "frontend/src/components/charts",
    "frontend/src/components/dialogs",
    "frontend/src/components/inputs",
    "frontend/src/components/loading",
    "frontend/src/features",
    "frontend/src/features/dataset",
    "frontend/src/features/research",
    "frontend/src/features/experiments",
    "frontend/src/features/knowledge",
    "frontend/src/features/recommendation",
    "frontend/src/hooks",
    "frontend/src/services",
    "frontend/src/store",
    "frontend/src/types",
    "frontend/src/utils",
]

# Frontend files per frontend-folder-structure.md
FRONTEND_FILES = [
    "frontend/src/services/apiClient.ts",
    "frontend/src/services/websocketClient.ts",
    "frontend/src/store/datasetStore.ts",
    "frontend/src/store/researchStore.ts",
    "frontend/src/store/experimentStore.ts",
    "frontend/src/store/userStore.ts",
    "frontend/src/pages/LandingPage/index.tsx",
    "frontend/src/pages/DatasetUploadPage/index.tsx",
    "frontend/src/pages/DatasetIntelligencePage/index.tsx",
    "frontend/src/pages/ResearchTimelinePage/index.tsx",
    "frontend/src/pages/ExperimentExplorerPage/index.tsx",
    "frontend/src/pages/KnowledgeEvolutionPage/index.tsx",
    "frontend/src/pages/FinalRecommendationPage/index.tsx",
]

def main():
    print("Bootstrapping repository structure per folder-structure.md specs...")
    
    # Create backend directories with __init__.py
    for d in BACKEND_DIRS:
        dir_path = BASE_DIR / d
        dir_path.mkdir(parents=True, exist_ok=True)
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Package initializer\n")
            print(f"Created package: {d}/__init__.py")

    # Create backend python modules
    for f in BACKEND_FILES:
        file_path = BASE_DIR / f
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_name = file_path.name
            file_path.write_text(f'"""Module: {file_name}"""\n')
            print(f"Created backend module: {f}")

    # Create frontend directories
    for d in FRONTEND_DIRS:
        dir_path = BASE_DIR / d
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create frontend files
    for f in FRONTEND_FILES:
        file_path = BASE_DIR / f
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.write_text(f"// {file_path.name}\nexport {{}};\n")
            print(f"Created frontend file: {f}")

    print("Bootstrap completed successfully!")

if __name__ == "__main__":
    main()
