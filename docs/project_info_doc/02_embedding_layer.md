# Phase 2 — Embedding Layer

## Overview

This phase introduced the **Embedding Layer** of the Trader Intelligence AI Copilot (TIAC).

The purpose of this layer is to convert enterprise knowledge documents into dense vector representations that can later be stored inside a vector database (Chroma) and retrieved using semantic similarity.

The embedding layer is designed using the same architectural principles as the LLM layer:

- Interface-based programming
- Factory Pattern
- Dependency Inversion
- Swappable providers

This ensures the rest of the application remains independent of any specific embedding provider.

---

# Why Do We Need Embeddings?

Large Language Models cannot efficiently search hundreds of documents.

Instead, every document is converted into a numerical representation called an **embedding**.

Example:

```
"The trader is using excessive leverage."
```

↓

```
[-0.143,
 0.287,
 ...
 3072 values]
```

Documents with similar meanings generate similar vectors.

Later, when a user asks a question, the same embedding process is applied to the query.

The vector database retrieves the most semantically similar document chunks.

---

# Architecture

```
Application
      │
      ▼
BaseEmbeddingProvider
      │
      ▼
GeminiEmbeddingProvider
      │
      ▼
Google Gemini Embedding API
```

The application never communicates directly with Google's embedding API.

Instead, it depends on the abstraction provided by `BaseEmbeddingProvider`.

---

# Project Structure

```
embeddings/
│
├── base.py
├── gemini.py
├── factory.py
└── __init__.py
```

---

# Components

## 1. BaseEmbeddingProvider

Defines the contract for all embedding providers.

Responsibilities:

- Embed multiple documents
- Embed a search query

Current interface:

```python
embed_documents(documents: list[Document])
embed_query(text: str)
```

Using `Document` objects instead of raw strings preserves metadata throughout the ingestion pipeline.

---

## 2. GeminiEmbeddingProvider

Concrete implementation using Google's Gemini Embedding API.

Responsibilities:

- Initialize the embedding model
- Convert `Document` objects into text
- Generate embeddings
- Return vector representations

The provider contains all provider-specific implementation details.

Business logic never imports `GoogleGenerativeAIEmbeddings`.

---

## 3. Factory

The factory creates the configured embedding provider.

```
Configuration

↓

Factory

↓

GeminiEmbeddingProvider
```

Future providers can be added without changing business logic.

Examples:

- OpenAI Embeddings
- Azure OpenAI Embeddings
- Voyage AI
- Cohere
- Hugging Face

---

# Configuration

The embedding layer is configured through environment variables.

Example:

```env
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=gemini-embedding-001
```

The configuration is loaded using Pydantic Settings.

---

# Why Use Documents Instead of Strings?

A common implementation converts documents into plain strings before generating embeddings.

Example:

```
Document

↓

String

↓

Embedding
```

This approach loses valuable metadata.

Instead, TIAC keeps the workflow as:

```
Document

↓

Embedding Provider

↓

Embedding
```

The provider extracts `page_content` internally while preserving metadata such as:

- Source file
- Page number
- Document name

This enables future features like source citations and document tracing.

---

# Design Principles Followed

## Interface-Based Programming

Business logic depends on:

```
BaseEmbeddingProvider
```

instead of

```
GoogleGenerativeAIEmbeddings
```

---

## Factory Pattern

Embedding providers are selected using configuration.

```
Gemini

↓

OpenAI

↓

Voyage AI

↓

Azure OpenAI
```

No business logic changes are required.

---

## Separation of Concerns

Embedding generation is isolated from:

- Document loading
- Document processing
- Vector storage
- Retrieval
- Prompt building

Each layer has a single responsibility.

---

## Dependency Inversion

Application services depend on abstractions rather than concrete implementations.

This improves:

- Testability
- Maintainability
- Extensibility

---

# Testing

A simple verification script was created:

```
scripts/test_embeddings.py
```

The script generates an embedding for a sample query.

Example:

```python
vector = embedding_provider.embed_query(
    "What is risk management?"
)
```

Output:

```
Embedding dimension: 3072
```

This confirms:

- Configuration is loaded correctly.
- Gemini API authentication works.
- The embedding provider is functioning as expected.

---

# Challenges Encountered

## 1. Deprecated Embedding Model

Originally:

```
models/text-embedding-004
```

returned:

```
404 NOT_FOUND
```

Google has deprecated this model for new API versions.

Solution:

```
gemini-embedding-001
```

---

## 2. Updated LangChain API

The latest version of `langchain-google-genai` uses:

```python
api_key=
```

instead of:

```python
google_api_key=
```

The implementation was updated accordingly.

---

# Current Architecture

```
FastAPI

↓

Chat Service

↓

LLM Provider

↓

Gemini

────────────────────────────

Embedding Provider

↓

Gemini Embeddings
```

Both infrastructure components now follow the same architecture, making the system consistent and easily extensible.

---

# Next Phase

The next phase introduces the **Knowledge Layer**.

Pipeline:

```
Enterprise PDFs

↓

Document Loader

↓

Document Processor

↓

Embeddings

↓

Chroma Vector Database
```

This will establish the foundation for Retrieval-Augmented Generation (RAG).

---

# Status

## Completed

- Embedding abstraction
- Gemini embedding provider
- Factory implementation
- Configuration
- Environment integration
- Query embedding
- Provider testing

## Next Milestone

Knowledge Ingestion Pipeline

```
PDFs

↓

Documents

↓

Chunks

↓

Vectors

↓

Chroma
```

This marks the transition from a simple LLM-powered application to a production-ready RAG system.