# AI Business Intelligence Platform

Enterprise-oriented AI Business Intelligence platform.

## Current Features

-   FastAPI
-   Semantic Search
-   Knowledge Engine
-   FAISS Vector Store
-   Persistent Vector Storage
-   Automatic Index Restore
-   Retrieval Engine

## Architecture

``` text
Client -> FastAPI -> Knowledge Engine -> Embeddings -> FAISS -> Persistent Storage

                ┌──────────────────────┐
                │      FastAPI API     │
                └──────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     Analytics Engine          AI Layer
              │                         │
              │                Knowledge Engine
              │                         │
              │                Embedding Service
              │                         │
              │                FAISS Vector Store
              │                         │
              └────────────┬────────────┘
                           │
                    SQLite Database


```

## Tech Stack

-   Python
-   FastAPI
-   SQLAlchemy
-   SQLite
-   FAISS
-   Sentence Transformers

## Roadmap

-   Advanced Retrieval
-   RAG
-   LLM Integration
-   Docker
-   CI/CD
