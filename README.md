# AI Business Intelligence Platform

Enterprise-grade AI Business Intelligence Platform powered by Multi-Agent AI, Semantic Retrieval, SQL Intelligence, and Enterprise Analytics.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Enterprise-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Data%20Warehouse-blue)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-orange)
![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

# Overview

AI Business Intelligence Platform is an enterprise-oriented Business Intelligence Copilot that combines semantic retrieval, SQL analytics, and multi-agent orchestration into a single AI system.

Instead of acting as a traditional RAG chatbot, the platform understands business questions, retrieves relevant knowledge, executes structured analytics, generates SQL when required, and produces grounded responses through a modular enterprise pipeline.

---

# Highlights

* Enterprise Multi-Agent AI Architecture
* Natural Language Business Analytics
* SQL Intelligence
* Retrieval-Augmented Generation (RAG)
* FAISS Semantic Search
* Enterprise Copilot Engine
* Runtime Execution Context
* PostgreSQL Data Warehouse
* Star Schema Analytics
* Provider-independent LLM Layer

---

# Architecture

```text
                                   User
                                     │
                                     ▼
                             Copilot Service
                                     │
                                     ▼
                          Enterprise Copilot Engine
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          ▼                          ▼                          ▼
 Intent Classification        Context Builder          Execution Context
                                     │
                                     ▼
                      Planner Agent
                             │
                             ▼
                    Retriever Agent
                             │
                             ▼
                    Analytics Agent
                             │
                             ▼
                       SQL Agent
                             │
                             ▼
                    Response Agent
                             │
                             ▼
                     Prompt Builder
                             │
                             ▼
                        LLM Provider
                             │
                             ▼
                   Enterprise AI Response
```

---

# Key Features

## AI

* Multi-Agent AI Copilot
* Intent Classification
* Prompt Builder
* Provider-independent LLM Layer
* Enterprise Response Generation

## Retrieval

* Semantic Search
* FAISS Vector Database
* Embedding Retrieval
* Context Builder
* Citation Support

## Analytics

* Business KPI Analysis
* SQL Analytics
* Natural Language Queries
* Data Warehouse Integration

## Runtime

* Execution Context
* Runtime Pipeline
* Agent Orchestration
* Modular Architecture

---

# Technology Stack

| Layer        | Technology            |
| ------------ | --------------------- |
| Backend      | FastAPI               |
| Language     | Python 3.12           |
| Database     | PostgreSQL            |
| ORM          | SQLAlchemy            |
| Validation   | Pydantic v2           |
| Vector Store | FAISS                 |
| Embeddings   | Sentence Transformers |
| AI           | Enterprise Copilot    |
| Architecture | Multi-Agent           |
| Testing      | Pytest + Manual Tests |

---

# Project Structure

```text
app
│
├── routers
├── schemas
├── models
├── utils
│
└── services
    ├── analytics
    ├── etl
    ├── vector_store
    ├── llm
    │
    └── ai
        └── copilot
            ├── engine.py
            ├── service.py
            ├── context_runtime
            ├── prompt.py
            ├── intent.py
            ├── context.py
            │
            └── agents
                ├── planner
                ├── retriever
                ├── analytics
                ├── sql
                └── response
```

---

# Quick Start

Clone the repository

```bash
git clone https://github.com/Mehdiest/AI-Business-Intelligence-Platform.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
uvicorn app.main:app --reload
```

Open Swagger

```text
http://localhost:8000/docs
```
# Enterprise Workflow

```text
User Question
      │
      ▼
Intent Classification
      │
      ▼
Planner Agent
      │
      ▼
Retriever Agent
      │
      ▼
Analytics Agent
      │
      ▼
SQL Agent
      │
      ▼
Response Agent
      │
      ▼
Prompt Builder
      │
      ▼
LLM Provider
      │
      ▼
Enterprise Business Response
```

---

# SQL Intelligence

The SQL Agent transforms natural language questions into executable SQL queries using a modular pipeline.

```text
Natural Language
        │
        ▼
 SQL Planner
        │
        ▼
SQL Generator
        │
        ▼
SQL Validator
        │
        ▼
 SQL Executor
        │
        ▼
SQL Formatter
        │
        ▼
 Business Result
```

Current capabilities include:

* SQL planning
* SQL generation
* SQL validation
* Safe query execution
* Result formatting
* Enterprise SQL orchestration

---

# Multi-Agent Components

| Agent     | Responsibility                |
| --------- | ----------------------------- |
| Planner   | Plans execution strategy      |
| Retriever | Retrieves semantic knowledge  |
| Analytics | Produces business insights    |
| SQL       | Executes structured analytics |
| Response  | Builds the final AI response  |

---

# Current Capabilities

* Enterprise Business Intelligence Copilot
* Multi-Agent AI Architecture
* Retrieval-Augmented Generation (RAG)
* Semantic Search with FAISS
* PostgreSQL Data Warehouse
* SQL Intelligence
* Business KPI Analysis
* Runtime Execution Context
* Enterprise Prompt Pipeline
* Provider-independent LLM Layer

---

# Testing

The repository contains independent manual tests for every major component.

Available validation suites include:

* Copilot Pipeline
* Planner Agent
* Retriever Agent
* Analytics Agent
* SQL Planner
* SQL Generator
* SQL Agent
* Response Agent
* Multi-Agent Pipeline
* Enterprise Runtime
* Phase 7 Audit

Each module can be validated independently before being integrated into the full execution pipeline.

---

# Development Roadmap

| Phase                              | Status         |
| ---------------------------------- | -------------- |
| Phase 1 — Foundation               | ✅ Complete     |
| Phase 2 — Data Platform            | ✅ Complete     |
| Phase 3 — Business Intelligence    | ✅ Complete     |
| Phase 4 — Semantic Retrieval       | ✅ Complete     |
| Phase 5 — Enterprise Copilot       | ✅ Complete     |
| Phase 6 — RAG Integration          | ✅ Complete     |
| Phase 7 — Multi-Agent Architecture | ✅ Complete     |
| Phase 7.5 — Production Polish      | 🚧 In Progress |
| Phase 8 — Production Features      | ⏳ Planned      |

---

# Planned Features

The next development phase focuses on production readiness.

Planned improvements include:

* Docker Support
* Redis Cache
* Streaming Responses
* Conversation Memory
* OpenAI Integration
* Ollama Integration
* Azure OpenAI Support
* CI/CD Pipeline
* Monitoring
* Observability
* Prompt Versioning
* Enterprise Logging

---

# Documentation

Additional technical documentation will be available inside the `docs/` directory.

Planned documentation includes:

```text
docs/

├── ARCHITECTURE.md
├── AI_AGENTS.md
├── SQL_ENGINE.md
├── RUNTIME.md
├── DEVELOPMENT.md
└── ROADMAP.md
```

---

# Why This Project?

This project demonstrates how modern enterprise AI systems combine:

* Backend Engineering
* Data Engineering
* Business Intelligence
* Retrieval-Augmented Generation
* SQL Intelligence
* Multi-Agent Systems

within a clean, modular, production-oriented architecture.

Instead of implementing a simple AI chatbot, the platform focuses on enterprise analytics, structured reasoning, and scalable AI orchestration.

---

# Contributing

Contributions, suggestions, and discussions are welcome.

Feel free to open an Issue or submit a Pull Request.

---

# License

This project is licensed under the MIT License.

---

# Author

**Mehdi Esteghlal**

AI • Data Science • Machine Learning • Business Intelligence • Enterprise Analytics

---

⭐ If you found this project useful, consider giving the repository a star.
