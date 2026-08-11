# DataPilot-AI 🚀
### Autonomous AI Data Science & Machine Learning Research Engine

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![Framework](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![Orchestration](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)
![Frontend](https://img.shields.io/badge/Next.js-14.2-black.svg)
![LLM Provider](https://img.shields.io/badge/OpenRouter-Nemotron--3.5-purple.svg)
![Tests](https://img.shields.io/badge/tests-69%20passed%20(100%25)-success.svg)

**DataPilot-AI** is an production-grade, autonomous AI research copilot that transforms raw tabular datasets into optimized, production-ready machine learning pipelines and actionable scientific reports. 

By unifying **LLM multi-agent reasoning**, **LangGraph state machine orchestration**, **statistical data profiling**, and **scikit-learn deterministic execution**, DataPilot-AI explores model architectures, prevents target memorization / data leakage, evaluates pipeline stability, and exports cleaned preprocessed CSV datasets in seconds.

---

## 🌟 Key Features

- 🧠 **Autonomous AI Multi-Agent Council**: 5 specialized AI agents (`DatasetUnderstandingAgent`, `ConstraintGoalAnalyzer`, `StrategyPlannerAgent`, `ResearchDirectorAgent`, `ReportGeneratorAgent`) driven by **OpenRouter LLMs** (`nvidia/nemotron-3.5-lightning:free`) with rate limiting and zero-downtime rule-based fallbacks.
- 🎼 **LangGraph State Machine Engine**: Stateful cyclic workflow controlling iterative research loops, iteration budget enforcement (max 5 iterations), and early convergence detection ($0.5\%$ metric threshold).
- 🔬 **Deterministic ML Execution Engine**: Automatic imputation, categorical encoding, feature scaling, and adaptive cross-validation (`StratifiedKFold` with fallback to `KFold` for small sample sizes).
- 🛡️ **Zero Data Leakage Identifier Preservation**: Automatically identifies non-predictive metadata columns (`id`, `name`, `customer_id`) and isolates them during model training to eliminate fake $1.00$ accuracy, while re-attaching them intact in exported CSV artifacts.
- 🏆 **Multi-Objective Composite Ranking Engine**: Ranks candidate pipelines across 5 composite dimensions: **Normalized Metric ($35\%$)**, **Generalization Gap ($25\%$)**, **Fold Variance ($20\%$)**, **Runtime Efficiency ($10\%$)**, and **Business Constraint Compliance**.
- 📡 **Real-Time WebSockets Telemetry**: Streams live terminal logs and status events (`job.status_changed`, `experiment.completed`, `knowledge.updated`, `job.completed`) over `/ws/jobs/{job_id}`.
- 📥 **1-Click Artifact Exports**: Instant downloads for preprocessed cleaned CSV datasets (`.csv`), trained pipeline binaries (`.pkl`), Markdown reports (`.md`), and Glassmorphism HTML web reports (`.html`).

---

## 🌊 High-Level Architecture & Real Flow Diagrams

### 1. End-to-End System Data Flow

```mermaid
flowchart TD
    %% Styling
    classDef client fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef gateway fill:#1e1e38,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef graph fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    classDef agents fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#f8fafc;
    classDef mlfill fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef storage fill:#451a03,stroke:#fb923c,stroke-width:2px,color:#f8fafc;

    User["👤 User / Next.js Dashboard"] :::client -->|1. Upload Raw CSV/Parquet| API["🔌 FastAPI REST Gateway"] :::gateway
    API -->|2. Save File & Profile| Profiler["🔬 Profiling Engine"] :::mlfill
    Profiler -->|3. Generate SemanticProfile| JobMgr["⚙️ JobManager (Async Worker)"] :::gateway

    JobMgr -->|4. Launch Async Worker| LangGraph["🎼 LangGraph State Machine"] :::graph
    
    subgraph Iterative_Research_Loop ["🔄 Iterative Autonomous Research Loop"]
        LangGraph -->|5. Dataset Understanding| Agent1["🧠 DatasetUnderstandingAgent"] :::agents
        Agent1 -->|6. Plan Experiments| Agent2["🧠 StrategyPlannerAgent"] :::agents
        Agent2 -->|7. Execute ML Pipelines| MLEngine["🔬 ML Execution Engine"] :::mlfill
        MLEngine -->|8. Evaluate & Rank| EvalEngine["🏆 Evaluation Engine"] :::mlfill
        EvalEngine -->|9. Director Decision| Agent3["🧠 ResearchDirectorAgent"] :::agents
        Agent3 -->|10. Check Gain & Budget| Router{"🚦 route_next Router"} :::graph
        Router -- Gain > 0.5% & Budget Left --> Agent2
    end

    Router -- Converged / Stop --> ReportAgent["🧠 ReportGeneratorAgent"] :::agents
    ReportAgent -->|11. Synthesize Artifacts| Exporter["📦 ArtifactExporter"] :::storage

    Exporter -->|12. Export .csv, .pkl, .md, .html| Storage[("💾 Disk Storage & SQLite DB")] :::storage
    JobMgr <-->|13. Real-Time Telemetry| WS["📡 WebSocket Broadcaster"] :::gateway
    WS <-->|14. Live Event Console Stream| User
```

---

### 2. LangGraph State Machine Topology

```mermaid
stateDiagram-v2
    [*] --> Profiling : Job Dispatched
    
    state Profiling {
        [*] --> DelimiterSniffer
        DelimiterSniffer --> SchemaAnalyzer
        SchemaAnalyzer --> QualityAnalyzer
    }

    Profiling --> Understanding : SemanticProfile Created

    state Understanding {
        [*] --> DatasetUnderstandingAgent
        DatasetUnderstandingAgent --> MissionBrief
    }

    Understanding --> Planning : MissionBrief Created

    state Planning {
        [*] --> StrategyPlannerAgent
        StrategyPlannerAgent --> ExperimentPlan
    }

    Planning --> Execution : ExperimentPlan Dispatched

    state Execution {
        [*] --> SeparateMetaCols
        SeparateMetaCols --> FitPipeline
        FitPipeline --> AdaptiveCV
    }

    Execution --> Evaluation : Batch Results Collected

    state Evaluation {
        [*] --> ScreenConstraints
        ScreenConstraints --> Composite5DRanking
        Composite5DRanking --> MineKnowledgeFindings
    }

    Evaluation --> Directing : EvaluationReport Created

    state Directing {
        [*] --> ResearchDirectorAgent
    }

    Directing --> RouterChoice : Evaluate route_next()

    state RouterChoice <<choice>>
    RouterChoice --> Planning : Continue / Refine (Budget Left)
    RouterChoice --> Reporting : Stop / Converged
    RouterChoice --> Failed : Execution Error

    state Reporting {
        [*] --> ReportGeneratorAgent
        ReportGeneratorAgent --> MarkdownGen
        MarkdownGen --> HTMLGen
    }

    Reporting --> Completed : Persist DB & Export Files
    Failed --> [*]
    Completed --> [*]
```

---

### 3. OpenRouter LLM Provider & Fallback Engine

```mermaid
flowchart LR
    Agent["🧠 Agent Prompt"] --> Client["LLMClient.generate_structured()"]
    Client --> Schema["_clean_json_schema()\n(Strips $defs & $schema)"]
    
    Schema --> P1{"1. OpenRouter API Key?"}
    P1 -- Yes --> OpenRouter["OpenRouter API\n(nvidia/nemotron-3.5-lightning:free)"]
    P1 -- No --> P2{"2. OpenAI API Key?"}
    
    P2 -- Yes --> OpenAI["OpenAI API\n(gpt-4o-mini)"]
    P2 -- No --> P3{"3. Gemini API Key?"}
    
    P3 -- Yes --> Gemini["Google Gemini API\n(14 RPM Rate Limiter)"]
    P3 -- No --> Fallback["4. Rule-Based Fallback\n(Zero-Downtime Response)"]

    OpenRouter --> Validate["model_validate_json()"]
    OpenAI --> Validate
    Gemini --> Validate
    Fallback --> Validate
    Validate --> Output["Structured Pydantic Model"]
```

---

## 📚 10-Phase Documentation Directory Index

Comprehensive, story-driven teacher documentation for every phase is available in the [`docs/`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs) folder:

| Phase | Title | Documentation Link |
| :--- | :--- | :--- |
| **Overview** | **Master System Architecture Overview** | [`docs/00-master-system-architecture.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/00-master-system-architecture.md) |
| **Diagrams** | **High-Level Visual Architecture Diagrams** | [`docs/system-architecture-diagrams.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/system-architecture-diagrams.md) |
| **Phase 01** | Contracts & Pydantic Schemas | [`docs/phase-01-contracts-schemas.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-01-contracts-schemas.md) |
| **Phase 02** | Database Layer & ORM Repositories | [`docs/phase-02-database-layer.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-02-database-layer.md) |
| **Phase 03** | Core Config, Middleware & Exceptions | [`docs/phase-03-core-config-middleware.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-03-core-config-middleware.md) |
| **Phase 04** | ML Execution Engine & Scikit-Learn Pipelines | [`docs/phase-04-api-services-websockets.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-04-api-services-websockets.md) |
| **Phase 05** | AI Multi-Agent System & OpenRouter LLMs | [`docs/phase-05-ai-agents-llm-system.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-05-ai-agents-llm-system.md) |
| **Phase 06** | Profiling Engine & Data Diagnostics | [`docs/phase-06-profiling-engine.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-06-profiling-engine.md) |
| **Phase 07** | LangGraph State Machine Graph Engine | [`docs/phase-07-langgraph-orchestration.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-07-langgraph-orchestration.md) |
| **Phase 08** | Evaluation Engine & Composite Model Ranking | [`docs/phase-08-evaluation.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-08-evaluation.md) |
| **Phase 09** | Application Services, API Gateway & WebSockets | [`docs/phase-09-services-api.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-09-services-api.md) |
| **Phase 10** | Final Research Reports & Artifact Exporters | [`docs/phase-10-reports.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-10-reports.md) |

---

## ⚡ Quickstart Guide

### 1. Environment Setup
Create a `.env` file in the root directory:
```env
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./datapilot.db
STORAGE_DIR=storage

# OpenRouter LLM Configuration
OPEN_ROUTER=your_openrouter_api_key_here
MODEL_NAME=nvidia/nemotron-3.5-lightning:free
```

### 2. Start the Backend API Server
```bash
# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI application on http://localhost:8000
uvicorn backend.main:app --reload --port 8000
```

### 3. Start the Next.js Frontend Dashboard
```bash
cd frontend

# Install Node dependencies
npm install

# Launch Next.js dev server on http://localhost:3000
npm run dev
```

### 4. Run the Full Test Suite
```bash
# Run all 69 unit & integration tests
pytest
```

---

## 🔌 API Reference Overview

| Endpoint Path | Method | Description |
| :--- | :--- | :--- |
| `POST /api/v1/upload` | `POST` | Upload raw CSV/Parquet file & return semantic profile |
| `POST /api/v1/jobs/start` | `POST` | Start autonomous AI research job in background |
| `GET /api/v1/jobs/{job_id}` | `GET` | Retrieve live job status, stage, and progress % |
| `GET /api/v1/experiments/{job_id}` | `GET` | Retrieve experiment leaderboard rankings & metrics |
| `GET /api/v1/reports/{job_id}` | `GET` | Retrieve final recommendation report |
| `GET /api/v1/reports/{job_id}/download-dataset` | `GET` | **Export preprocessed cleaned CSV dataset artifact** |
| `WS /ws/jobs/{job_id}` | `WS` | Real-time WebSocket event subscription channel |

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
