# Phase 5 — Retrieval Layer

## Overview

The Retrieval Layer is responsible for finding the most relevant knowledge from the vector database.

Unlike traditional keyword search, retrieval uses semantic similarity.

```
User Question

↓

Retriever

↓

Vector Store

↓

Relevant Documents
```

The retriever becomes the bridge between the knowledge base and the Large Language Model.

---

# Why Do We Need a Retriever?

Without retrieval

```
User

↓

LLM

↓

Answer
```

The LLM relies only on its pretrained knowledge.

With retrieval

```
User

↓

Retriever

↓

Knowledge Base

↓

LLM

↓

Grounded Answer
```

The answer is based on enterprise documents instead of the model's memory.

---

# Architecture

```
Application

↓

BaseRetriever

↓

VectorRetriever

↓

Vector Store

↓

Chroma
```

The application never communicates directly with Chroma.

It only depends on the retriever abstraction.

---

# Project Structure

```
retrieval/

├── base.py
├── vector_retriever.py
├── factory.py
└── __init__.py
```

---

# Components

## 1. BaseRetriever

Defines the retrieval interface.

Current method

```python
retrieve(
    query,
    k=5,
)
```

Returns

```
list[Document]
```

---

## 2. VectorRetriever

Concrete implementation using the vector store.

Responsibilities

- Receive a user query
- Perform similarity search
- Return the most relevant documents

It does not:

- Call the LLM
- Build prompts
- Format responses

---

## 3. Factory

Creates the configured retriever.

```
Configuration

↓

Factory

↓

VectorRetriever
```

Future retrieval strategies can easily replace the implementation.

Examples

- Hybrid Retrieval
- Metadata Retrieval
- Multi-stage Retrieval
- Ensemble Retrieval

---

# Retrieval Process

Current workflow

```
User Question

↓

Embedding

↓

Similarity Search

↓

Top K Documents
```

The retriever returns LangChain `Document` objects.

Each document contains

- Page content
- Metadata

Example

```python
Document(
    page_content="...",
    metadata={
        "category": "...",
        "page": 12,
        "document_name": "...",
    }
)
```

---

# Why Return Documents?

Returning Document objects preserves metadata.

Later the AI can answer

```
According to

Risk Management.pdf

Page 12
```

This enables explainable AI and source attribution.

---

# Design Principles

## Separation of Concerns

Retriever only retrieves.

It does not

- Generate answers
- Build prompts
- Perform reasoning

---

## Dependency Injection

Application services receive a retriever.

Example

```python
ChatService(
    retriever=...
)
```

instead of creating one internally.

---

## Interface-Based Programming

Business logic depends on

```
BaseRetriever
```

instead of

```
VectorRetriever
```

Future retrieval methods become plug-and-play.

---

# Current Retrieval Strategy

Semantic Similarity Search

```
Question

↓

Embedding

↓

Nearest Neighbors

↓

Top K Results
```

This forms the foundation of Retrieval-Augmented Generation.

---

# Validation

Retrieval was verified independently before integrating with the LLM.

Example

```python
retriever.retrieve(
    "How can I reduce trading risk?"
)
```

Returned

- Relevant chunks
- Correct metadata
- Expected document categories

Testing retrieval independently isolates retrieval quality from LLM performance.

---

# Current Status

Completed

- Retriever abstraction
- VectorRetriever implementation
- Factory implementation
- Similarity search
- Retrieval testing

---

# Next Phase

Prompt Construction.

```
User Question

↓

Retriever

↓

Context Builder

↓

LLM

↓

Grounded Answer
```

This completes the final step before building the production RAG chatbot.