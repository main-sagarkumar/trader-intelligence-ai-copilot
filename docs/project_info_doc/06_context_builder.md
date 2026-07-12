# Context Builder

## Overview

The Context Builder transforms retrieved LangChain `Document` objects into a structured context that can be safely consumed by the LLM.

## Responsibilities

- Format retrieved documents
- Preserve metadata
- Build source references
- Return immutable context objects

## Input

list[Document]

## Output

ContextResult

### ContextResult

Contains:

- context
- sources

### SourceReference

Contains:

- document_name
- category
- page
- relative_path

## Architecture

Retriever
↓

ContextBuilder
↓

ContextResult
↓

PromptBuilder

## Design Decisions

- Immutable dataclasses
- Metadata preserved
- No LLM dependency
- No Retriever dependency
- Single Responsibility Principle

## Future Usage

- Source citations
- Hybrid retrieval
- Memory
- Evaluation
- Observability

## Next Module

ChatService RAG Orchestration