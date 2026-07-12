# Phase 4 — Vector Store (Chroma)

## Overview

This phase introduces the **Vector Store Layer** of the Trader Intelligence AI Copilot.

The vector store is responsible for persisting document embeddings and performing semantic similarity search.

This layer sits between the Knowledge Layer and the Retrieval Layer.

```
Knowledge

↓

Vector Store

↓

Retriever
```

The implementation follows the same architectural principles used throughout the project:

- Interface-based programming
- Factory Pattern
- Dependency Injection
- Provider abstraction

---

# Why Do We Need a Vector Store?

Large Language Models cannot efficiently search hundreds of documents.

Instead, every document chunk is converted into an embedding and stored inside a vector database.

Example

```
Trading Psychology

↓

Chunk

↓

Embedding

↓

Stored in Chroma
```

Later, when a user asks a question:

```
User Question

↓

Embedding

↓

Similarity Search

↓

Top Matching Chunks
```

The LLM only receives the most relevant chunks instead of the entire document collection.

---

# Architecture

```
Application

↓

BaseVectorStore

↓

ChromaVectorStore

↓

Chroma Database
```

Business logic never communicates directly with Chroma.

All interactions happen through the `BaseVectorStore` abstraction.

---

# Project Structure

```
vectorstore/

├── base.py
├── chroma.py
├── factory.py
└── pinecone.py
```

---

# Components

## 1. BaseVectorStore

Defines the contract for every vector database.

Current interface

```python
add_documents()

similarity_search()

reset()
```

This ensures every vector database behaves consistently.

Future implementations may include:

- Pinecone
- Qdrant
- Weaviate
- Milvus

without changing application logic.

---

## 2. ChromaVectorStore

Concrete implementation using Chroma.

Responsibilities

- Create collections
- Persist document embeddings
- Execute similarity search
- Reset collections

It does not:

- Load documents
- Split documents
- Generate prompts
- Call the LLM

Single Responsibility Principle is maintained.

---

## 3. Factory

Creates the configured vector store.

```
Configuration

↓

Factory

↓

ChromaVectorStore
```

Future vector databases can be selected using configuration without modifying business code.

---

# Why Chroma?

Chroma was selected because it:

- Runs locally
- Requires no infrastructure
- Integrates well with LangChain
- Is ideal for development and portfolio projects

Production deployments can later migrate to:

- Pinecone
- Qdrant
- Weaviate

without affecting the application layer.

---

# Configuration

Environment variables

```env
VECTOR_STORE_PROVIDER=chroma

CHROMA_PERSIST_DIRECTORY=data/chroma

CHROMA_COLLECTION_NAME=trader_knowledge
```

---

# Knowledge Ingestion

Documents are stored through the following pipeline.

```
PDFs

↓

Document Loader

↓

Document Processor

↓

Embeddings

↓

Chroma
```

Each chunk is stored together with metadata.

Example

```python
{
    "document_name": "...",
    "category": "...",
    "page": 12,
    "relative_path": "...",
}
```

Metadata enables future source citations and metadata filtering.

---

# Batch Ingestion

The Gemini Embedding API has request quotas.

To avoid rate limits, ingestion stores documents in batches.

```
Chunks

↓

Batch (90)

↓

Store

↓

Wait

↓

Next Batch
```

Advantages

- Avoids API throttling
- Improves stability
- Makes ingestion resumable
- Provides progress logging

This approach is commonly used in production ingestion pipelines.

---

# Design Principles

## Interface-Based Programming

Business logic depends on

```
BaseVectorStore
```

instead of

```
Chroma
```

---

## Factory Pattern

The configured vector database is created by a factory.

```
Configuration

↓

Factory

↓

Vector Store
```

---

## Dependency Injection

Services receive a vector store rather than creating one.

Example

```python
IngestService(
    vector_store=...
)
```

This simplifies testing and future extensions.

---

# Current Status

Completed

- Chroma integration
- Vector store abstraction
- Factory implementation
- Batch ingestion
- Similarity search
- Collection reset

---

# Next Phase

The Retrieval Layer.

```
User Question

↓

Retriever

↓

Top Matching Documents
```

This prepares the project for Retrieval-Augmented Generation (RAG).