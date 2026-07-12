# Trader Intelligence AI Copilot — Project Structure

## Overview

This is a Python 3.13 AI-powered trading intelligence backend built with FastAPI. It is designed around clean architecture principles and supports LLM chat, RAG-based knowledge retrieval, document ingestion, PostgreSQL, and vector databases.

## Directory Structure

```text
trader-intelligence-ai-copilot/
├── main.py                         # Temporary/root application entry point
├── pyproject.toml                  # Project configuration and dependencies
├── requirements.txt                # Pip dependency list
├── uv.lock                         # Locked dependency versions
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Multi-container local setup
├── .env.example                    # Environment-variable template
│
├── docs/
│   ├── architecture/
│   │   └── system_architecture.md  # Overall system design
│   ├── adr/                        # Architecture Decision Records
│   │   ├── ADR-001-ai-layer-separation.md
│   │   ├── ADR-002-hybrid-retrieval.md
│   │   └── ADR-003-structured-data-not-in-vector-db.md
│   ├── interview/                  # Architecture explanation notes
│   └── project_info_doc/           # Implementation and feature guides
│
└── src/
    └── trader_intelligence_ai_copilot/
        ├── api/                    # HTTP/API delivery layer
        │   ├── main.py             # FastAPI application setup
        │   ├── dependencies.py     # Dependency injection setup
        │   └── routers/
        │       ├── chat.py         # Chat API endpoints
        │       └── health.py       # Health-check endpoint
        │
        ├── application/            # Application use cases
        │   └── chat_service.py     # Orchestrates the chat workflow
        │
        ├── config/                 # Typed application configuration
        │   ├── base.py
        │   ├── settings.py
        │   ├── app/
        │   │   ├── application.py  # App-level settings
        │   │   ├── logging.py      # Logging settings
        │   │   └── security.py     # Security settings
        │   ├── infra/
        │   │   ├── credentials.py  # API keys and credentials
        │   │   ├── database.py     # PostgreSQL configuration
        │   │   ├── llm.py          # LLM provider configuration
        │   │   ├── embeddings.py   # Embedding configuration
        │   │   ├── vectorstore.py  # Vector database configuration
        │   │   └── monitoring.py   # Observability configuration
        │   └── enums/
        │       ├── environment.py  # Environment values
        │       └── providers.py    # Supported provider values
        │
        ├── llm/                    # LLM provider abstraction
        │   ├── base.py             # LLM interface
        │   ├── factory.py          # Provider selection
        │   └── gemini.py           # Google Gemini implementation
        │
        ├── embeddings/             # Embedding provider abstraction
        │   ├── base.py
        │   ├── factory.py
        │   └── gemini.py
        │
        ├── vectorstore/            # Vector database adapters
        │   ├── base.py
        │   ├── factory.py
        │   ├── chroma.py           # ChromaDB implementation
        │   └── pinecone.py         # Pinecone implementation
        │
        ├── knowledge/              # Knowledge-base and ingestion workflow
        │   ├── document_loader.py  # Reads PDF/other documents
        │   ├── text_splitter.py    # Splits documents into chunks
        │   ├── metadata.py         # Handles document metadata
        │   └── ingest_service.py   # Embeds and stores document chunks
        │
        ├── retrieval/              # Retrieval and hybrid-search logic
        ├── repositories/           # Database access layer
        │   ├── trader_repository.py
        │   └── postgres_trader_repository.py
        │
        ├── schemas/                # Pydantic request/response models
        │   ├── chat.py
        │   └── health.py
        │
        ├── scripts/
        │   └── ingest.py           # CLI entry point for document ingestion
        │
        ├── auth/                   # Authentication and authorization
        ├── chat/                   # Chat-domain components
        ├── trader/                 # Trading-domain components
        ├── memory/                 # Conversation-memory handling
        ├── prompts/                # Prompt templates
        ├── guardrails/             # Input/output safety checks
        ├── evaluation/             # RAG/LLM quality evaluation
        ├── monitoring/             # Metrics and monitoring
        ├── observability/          # Tracing and telemetry
        ├── core/                   # Shared constants, config, and logging
        └── utils/                  # Shared utility functions
            └── message_parser.py

Client
  → FastAPI Router
  → Chat Service
  → Retrieval / Repository / Memory
  → LLM Provider (Gemini)
  → API Response

Document
  → Document Loader
  → Text Splitter
  → Embedding Provider
  → Vector Store (ChromaDB or Pinecone)

Main Technologies
API: FastAPI and Uvicorn
LLM: Google Gemini through LangChain
Embeddings: Gemini embeddings
Vector databases: ChromaDB and Pinecone
Relational database: PostgreSQL with SQLAlchemy and Alembic
Observability: OpenTelemetry and MLflow
Evaluation: Ragas
Containerization: Docker and Docker Compose