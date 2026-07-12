# Trader Intelligence AI Copilot - ChatGPT Project Context

## Purpose

This document is the source-of-truth handoff for an AI assistant working on this repository. It describes the current modules, their responsibilities, their dependencies, and the gaps that remain. Treat the existing architecture as intentional unless a change request explicitly says otherwise.

The project is a Python 3.13 FastAPI backend for a trader-focused AI copilot. It uses Google Gemini for chat and embeddings, Chroma for the local vector store, and LangChain primitives for documents, prompts, messages, and integrations.

## Current architecture

```text
HTTP client
  -> FastAPI API routers
  -> application.ChatService
  -> llm.BaseLLMProvider -> llm.GeminiProvider -> Google Gemini

PDF knowledge documents
  -> knowledge.DocumentLoader
  -> knowledge.DocumentProcessor
  -> vectorstore.ChromaVectorStore
  -> Chroma persistent database

Future RAG chat path (components exist but are not yet connected)
  -> retrieval.VectorRetriever
  -> chat.ContextBuilder
  -> prompts.RAGPromptBuilder
  -> LLM
```

Important: `ChatService` currently sends only the user's question to the LLM. Retrieval, context building, source citations, and `RAGPromptBuilder` are implemented as independent components but are **not yet wired into the API chat flow**.

## Entry points

| Path | Role | Notes |
| --- | --- | --- |
| `main.py` | Root placeholder | Only prints a greeting; it is not the FastAPI entry point. |
| `src/trader_intelligence_ai_copilot/api/main.py` | FastAPI application | Creates `app` and registers the health and chat routers. |
| `scripts/ingest.py` | Knowledge ingestion CLI | Builds `IngestService` via API dependencies and ingests `data/documents`. |
| `scripts/test_*.py` | Manual component checks | Small executable tests for embeddings, retrieval, prompts, and context building. |

Run the API with:

```bash
uvicorn trader_intelligence_ai_copilot.api.main:app --reload
```

## API modules

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `api/main.py` | Creates FastAPI app; adds routers. | `config.get_settings`, chat and health routers |
| `api/routers/health.py` | Exposes `GET /health`; returns app name, version, and environment. | FastAPI, `schemas.HealthResponse`, settings |
| `api/routers/chat.py` | Exposes `POST /chat`; receives `ChatRequest`, calls `ChatService`, returns `ChatResponse`. | FastAPI dependency injection, `api.dependencies` |
| `api/dependencies.py` | Composition root for `ChatService` and `IngestService`. | LLM factory, vector-store factory, knowledge components |
| `schemas/chat.py` | Defines `ChatRequest(question)` and `ChatResponse(answer)`. | Pydantic |
| `schemas/health.py` | Defines `HealthResponse`. | Pydantic |

## Application and chat modules

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `application/chat_service.py` | The chat use case. Converts a question to a LangChain `HumanMessage`, then calls the configured LLM. | `llm.BaseLLMProvider`, `langchain_core.messages` |
| `chat/context_models.py` | Immutable result models: `SourceReference`, `ContextResult`, and `ChatResult`. | Python dataclasses |
| `chat/context_builder.py` | Converts retrieved LangChain documents into formatted context and source references. Missing metadata becomes `Unknown`. | `ContextResult`, `SourceReference`, LangChain `Document` |
| `prompts/rag_prompt.py` | Builds the trader-specific RAG prompt. The prompt requires `{context}` and `{question}`. | LangChain `ChatPromptTemplate` |
| `utils/message_parser.py` | Extracts text from an LLM `AIMessage`. | LangChain `AIMessage` |

## LLM modules

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `llm/base.py` | Abstract `BaseLLMProvider` interface; `generate_response(messages)` is asynchronous. | ABC, LangChain `BaseMessage` |
| `llm/gemini.py` | `GeminiProvider` implementation using `ChatGoogleGenerativeAI`; obtains credentials/model settings and normalizes the response to text. | `langchain_google_genai`, settings, `extract_text` |
| `llm/factory.py` | Cached provider factory, `get_llm()`. Selects provider from `LLM_PROVIDER`. | Settings, `LLMProvider`, `GeminiProvider` |

To add an LLM provider: implement `BaseLLMProvider`, add an enum value in `config/enums/providers.py`, and extend `llm/factory.py`.

## Knowledge ingestion modules

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `knowledge/document_loader.py` | Recursively loads every PDF in a directory using `PyPDFLoader`. Adds `document_name`, `category`, `relative_path`, `page`, and `total_pages` metadata. | `langchain_community`, LangChain `Document` |
| `knowledge/document_processor.py` | Splits loaded documents with `RecursiveCharacterTextSplitter`. Chunk size and overlap come from embedding settings. | `langchain_text_splitters`, settings |
| `knowledge/ingest_service.py` | Orchestrates load -> split -> reset vector store -> batch upsert. Batch size is 90 and waits 60 seconds between batches. | Loader, processor, `BaseVectorStore` |
| `scripts/ingest.py` | CLI wrapper that calls the dependency-created ingestion service. | `api.dependencies` |

Knowledge documents live in `data/documents/`. Their immediate parent directory becomes the document `category` metadata.

## Embeddings, vector store, and retrieval

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `embeddings/base.py` | Abstract embedding contract: document embeddings, query embedding, and LangChain-compatible embedding function. | LangChain `Embeddings`, `Document` |
| `embeddings/gemini.py` | Gemini embedding implementation using `GoogleGenerativeAIEmbeddings`. | `langchain_google_genai`, settings |
| `embeddings/factory.py` | Cached embedding provider factory. | Settings, provider enum |
| `vectorstore/base.py` | Abstract vector-store contract: add documents, similarity search, reset. | LangChain `Document` |
| `vectorstore/chroma.py` | Persistent local Chroma adapter. It creates/uses the configured collection and uses the configured embedding provider. | `langchain_chroma`, settings, embedding factory |
| `vectorstore/pinecone.py` | Reserved adapter location; not currently used by the factory. | None |
| `vectorstore/factory.py` | Cached vector-store factory. Current configured implementation is Chroma. | Settings, `ChromaVectorStore` |
| `retrieval/base.py` | Abstract retriever contract: `retrieve(query, k=5)`. | LangChain `Document` |
| `retrieval/vector_retriever.py` | Retrieves top-k documents with vector similarity search. | `BaseVectorStore` |
| `retrieval/factory.py` | Cached factory for the configured `VectorRetriever`. | Vector-store factory |

To add a vector store: implement `BaseVectorStore`, add a provider enum/configuration if needed, and extend `vectorstore/factory.py`.

## Configuration modules

Configuration uses Pydantic Settings. Each sub-configuration inherits `config.base.BaseConfig`; `config.settings.ApplicationSettings` aggregates them, and `get_settings()` returns one cached instance.

| Area | Modules | Primary environment variables |
| --- | --- | --- |
| Application | `config/app/application.py` | `APP_NAME`, `APP_VERSION`, `ENVIRONMENT`, `DEBUG` |
| Logging | `config/app/logging.py` | `LOG_LEVEL` |
| Security | `config/app/security.py` | Security values reserved/configured here |
| Database | `config/infra/database.py` | `DATABASE_PROVIDER`, `DATABASE_URL`, pool settings |
| Credentials | `config/infra/credentials.py` | Provider secrets, including Gemini credentials |
| LLM | `config/infra/llm.py` | `LLM_PROVIDER`, `LLM_MODEL` |
| Embeddings | `config/infra/embeddings.py` | `EMBEDDING_PROVIDER`, chunk size/overlap |
| Vector store | `config/infra/vectorstore.py` | `VECTORSTORE_PROVIDER` and store settings |
| Provider enums | `config/enums/providers.py` | Database, LLM, embedding, and vector-store provider names |

Use `.env.example` as the starting point. Never commit actual API keys or database URLs.

## Supporting and planned modules

The following package locations exist to preserve the target architecture. Most currently contain only `__init__.py` and should be implemented only when their use case is being added:

- `auth/` - authentication and authorization.
- `core/` - shared compatibility/config/logging utilities; currently not part of the primary path.
- `evaluation/` - RAG/LLM evaluation, intended for Ragas.
- `guardrails/` - input/output validation and safety controls.
- `memory/` - conversation memory and session state.
- `monitoring/` and `observability/` - metrics, traces, and MLflow/OpenTelemetry integration.
- `repositories/` - repository interfaces and a PostgreSQL trader repository; not connected to a request flow yet.
- `trader/` - trading-domain models and business rules.

## External dependencies

| Dependency group | Packages used |
| --- | --- |
| Web API | `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings` |
| LLM / RAG | `langchain`, `langchain-core`, `langchain-community`, `langchain-google-genai`, `google-generativeai` |
| Vector store | `chromadb`, `langchain-chroma` |
| Document processing | `pypdf`, `unstructured`, `langchain-text-splitters`, `tiktoken` |
| Data / database | `sqlalchemy`, `psycopg2-binary`, `alembic`, `pandas`, `numpy` |
| Security / HTTP | `python-jose`, `passlib`, `httpx` |
| Observability / quality | `loguru`, `mlflow`, `opentelemetry-api`, `opentelemetry-sdk`, `ragas` |
| Development | `pytest`, `pytest-cov`, `pytest-mock`, `ruff`, `black`, `isort`, `mypy`, `pre-commit` |

`pyproject.toml` is the primary package definition for the `uv` workflow. `requirements.txt` is retained as a pip-compatible dependency list; keep the two aligned if versions are changed.

## Implementation rules for future changes

1. Keep API routers thin: validation, dependency injection, and response shaping only.
2. Put use-case orchestration in `application/`.
3. Program against provider interfaces (`BaseLLMProvider`, `BaseEmbeddingProvider`, `BaseVectorStore`, `BaseRetriever`), not vendor implementations.
4. Obtain providers through their factories and settings through `get_settings()`; avoid constructing vendor clients in routers.
5. Preserve document metadata through splitting, retrieval, context creation, and source citation.
6. Connect retrieval to `ChatService` before claiming that `/chat` is RAG-enabled.
7. Add tests alongside every new non-trivial module or behavior.

## Recommended next integration: RAG chat

The intended ChatService dependency graph is:

```text
ChatService
  -> BaseRetriever.retrieve(question)
  -> ContextBuilder.build_context(documents)
  -> RAGPromptBuilder.build().format_messages(context, question)
  -> BaseLLMProvider.generate_response(messages)
  -> ChatResult(answer, sources)
```

This requires updating the `ChatService` constructor, `get_chat_service()` dependency, `ChatResponse` schema, and `/chat` router so the response includes `sources`.
