<div align="center">

# 🚀 DataPilot-AI
### Autonomous AI Data Science & Machine Learning Research Engine

[![Python Version](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-FF6F00?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![OpenRouter LLM](https://img.shields.io/badge/OpenRouter-Nemotron--3.5-7C3AED?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai)
[![Test Suite](https://img.shields.io/badge/Tests-69%20Passed%20(100%25)-2EA44F?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)

</div>

---

## 📌 Executive Overview

**DataPilot-AI** is a production-grade autonomous data science research engine designed to transform raw tabular datasets into optimized machine learning pipelines and scientific research reports without human intervention.

By integrating **LLM multi-agent consensus**, **LangGraph state machine orchestration**, **statistical diagnostics**, and **scikit-learn deterministic execution**, DataPilot-AI iteratively formulates hypotheses, executes candidate pipelines, isolates non-predictive metadata (preventing target memorization data leakage), and ranks models via a 5-dimensional multi-objective scoring matrix.

---

## 🏗️ Unified Master System Architecture Flow

The flowchart below details the single, end-to-end operational pipeline—from raw file ingestion to state machine execution, agent reasoning, ML evaluation, and multi-format artifact export.

```mermaid
flowchart TB
    subgraph Layer1 ["1. INGESTION & DIAGNOSTICS LAYER"]
        Client["🖥️ Next.js 14 Web Dashboard"] ==>|Raw CSV / Parquet Upload| REST["🔌 FastAPI REST Gateway"]
        REST ==>|Dispatch Stream| Profiler["🔬 Statistical Profiling Engine"]
        Profiler ==>|Generate SemanticProfile| JobMgr["⚙️ Async JobManager Worker"]
    end

    subgraph Layer2 ["2. LANGGRAPH STATE MACHINE LOOP"]
        JobMgr ==>|Spawn State Machine| Graph["🎼 LangGraph Engine"]
        
        subgraph AgentCouncil ["🧠 AI Multi-Agent Council (OpenRouter LLMs)"]
            Agent1["DatasetUnderstandingAgent"] --> Agent2["StrategyPlannerAgent"]
            Agent2 --> Agent3["ResearchDirectorAgent"]
            Agent3 --> Agent4["ReportGeneratorAgent"]
        end

        Graph ==>|Profile State| Agent1
        Agent1 ==>|Mission Brief| Agent2
        Agent2 ==>|Experiment Plan| MLExecutor["🔬 Scikit-Learn ML Execution Engine"]
        MLExecutor ==>|Cross-Validation Results| EvalEngine["🏆 5D Multi-Objective Evaluator"]
        EvalEngine ==>|Evaluation Report| Agent3
        
        Agent3 ==>|Check Gain & Budget| Router{"🚦 route_next Router"}
        Router -.->|Gain > 0.5% & Budget Left| Agent2
    end

    subgraph Layer3 ["3. PERSISTENCE & ARTIFACT EXPORT LAYER"]
        Router ==>|Converged / Budget Reached| Agent4
        Agent4 ==>|Synthesize Final Report| Exporter["📦 ArtifactExporter"]
        
        Exporter ==>|Pickled Pipeline (.pkl)| Models[("💾 Storage: storage/models/")]
        Exporter ==>|Cleaned CSV (.csv)| CleanCSV[("💾 Storage: storage/artifacts/")]
        Exporter ==>|Markdown & HTML Reports| Reports[("💾 Storage: storage/reports/")]
        Exporter ==>|Persist DB Records| Database[("🗄️ SQLite Database")]

        JobMgr <==>|Real-Time WebSockets Telemetry| WS["📡 WebSocket Broadcaster"]
        WS <==>|Live Event & Terminal Logs| Client
    end

    classDef clientStyle fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef gatewayStyle fill:#1e1e38,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef graphStyle fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    classDef agentStyle fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#f8fafc;
    classDef mlStyle fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef storageStyle fill:#451a03,stroke:#fb923c,stroke-width:2px,color:#f8fafc;

    class Client clientStyle;
    class REST,JobMgr,WS gatewayStyle;
    class Graph,Router graphStyle;
    class Agent1,Agent2,Agent3,Agent4 agentStyle;
    class Profiler,MLExecutor,EvalEngine mlStyle;
    class Exporter,Models,CleanCSV,Reports,Database storageStyle;
```

---

## ⚡ Core Technical Capabilities

| Capability | Architecture Specification | Technical Implementation |
| :--- | :--- | :--- |
| **Multi-Agent Consensus** | 5 Specialized Reasoning Agents | OpenRouter (`nvidia/nemotron-3.5-lightning:free`) with zero-downtime rule fallbacks |
| **State Orchestration** | Cyclic Directed Acyclic Graph (DAG) | LangGraph `StateGraph` enforcing max 5 iterations and $0.5\%$ gain threshold |
| **ML Execution Engine** | Scikit-Learn Pipeline Serialization | Automated imputation, encoding, scaling & adaptive `StratifiedKFold`/`KFold` CV |
| **Meta-Column Isolation** | Zero Data Leakage Enforcement | Identifies `id`/`name` entity columns, isolates during training, restores in export |
| **Composite Ranking** | 5-Dimensional Multi-Objective Matrix | $35\%$ metric, $25\%$ generalization, $20\%$ variance, $10\%$ runtime, rule screening |
| **Real-Time Telemetry** | Asynchronous Event Streaming | FastAPI WebSocket Channel (`/ws/jobs/{job_id}`) broadcasting status & logs |
| **Polyglot Artifacts** | Multi-Format Serialization | 1-click downloads for `.csv`, pickled `.pkl`, GitHub `.md`, and `.html` reports |

---

## 📚 10-Phase System Architecture Documentation Index

| Phase | Module Title | Document Reference | Primary Focus |
| :---: | :--- | :--- | :--- |
| **Index** | **Master System Architecture** | [`docs/00-master-system-architecture.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/00-master-system-architecture.md) | Full 10-Phase Executive System Index & Map |
| **Phase 01** | Contracts & Schemas | [`docs/phase-01-contracts-schemas.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-01-contracts-schemas.md) | Pydantic V2 Models, Enums & State Contracts |
| **Phase 02** | Database Layer & ORM | [`docs/phase-02-database-layer.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-02-database-layer.md) | SQLAlchemy 2.0 Repositories & SQLite Schemas |
| **Phase 03** | Core Config & Middleware | [`docs/phase-03-core-config-middleware.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-03-core-config-middleware.md) | Environment Config, Correlation ID & CORS |
| **Phase 04** | ML Execution Engine | [`docs/phase-04-api-services-websockets.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-04-api-services-websockets.md) | Scikit-Learn Pipelines & Adaptive CV Execution |
| **Phase 05** | AI Multi-Agent System | [`docs/phase-05-ai-agents-llm-system.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-05-ai-agents-llm-system.md) | 5 OpenRouter AI Agents & Fallback Logic |
| **Phase 06** | Profiling Engine | [`docs/phase-06-profiling-engine.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-06-profiling-engine.md) | Automated Data Diagnostics & Quality Checks |
| **Phase 07** | LangGraph Orchestration | [`docs/phase-07-langgraph-orchestration.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-07-langgraph-orchestration.md) | Stateful Graph State Machine & Router Rules |
| **Phase 08** | Evaluation Engine | [`docs/phase-08-evaluation.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-08-evaluation.md) | 5D Composite Scoring & Knowledge Mining |
| **Phase 09** | Services & API Gateway | [`docs/phase-09-services-api.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-09-services-api.md) | Async Workers, REST Endpoints & WebSockets |
| **Phase 10** | Final Reports & Exporters | [`docs/phase-10-reports.md`](file:///Users/akshitajariwala/Desktop/Akshita's%20Project/DataPilot-AI/docs/phase-10-reports.md) | Markdown/HTML Synthesizer & Artifact Export |

---

## ⚡ Quickstart Guide

### 1. Environment Setup
Configure your environment variables in `.env`:
```env
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./datapilot.db
STORAGE_DIR=storage

# OpenRouter LLM Settings
OPEN_ROUTER=sk-or-v1-your-key-here
MODEL_NAME=nvidia/nemotron-3.5-lightning:free
```

### 2. Launch Backend Gateway & Frontend Dashboard
```bash
# Terminal 1: Launch Backend API Server
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Launch Next.js Dashboard
cd frontend && npm run dev
```

### 3. Run Automated Verification Suite
```bash
# Execute unit and integration tests (69 passed)
pytest
```

---

## 🔌 Primary REST & WebSocket API Specification

| Endpoint | Method | Response Payload / Behavior |
| :--- | :---: | :--- |
| `/api/v1/upload` | `POST` | Processes dataset upload & returns initial `SemanticProfile` |
| `/api/v1/jobs/start` | `POST` | Spawns non-blocking async background research job |
| `/api/v1/jobs/{job_id}` | `GET` | Returns real-time status, execution stage & progress % |
| `/api/v1/experiments/{job_id}` | `GET` | Retrieves experiment leaderboard rankings & cross-validation metrics |
| `/api/v1/reports/{job_id}` | `GET` | Fetches synthesized recommendation report payload |
| `/api/v1/reports/{job_id}/download-dataset` | `GET` | **Serves cleaned CSV artifact attachment with ID columns preserved** |
| `/ws/jobs/{job_id}` | `WS` | Real-time WebSocket channel streaming live telemetry logs & events |

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
