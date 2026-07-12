# Trader Intelligence AI Copilot

A FastAPI backend that combines authenticated trader metrics from PostgreSQL
with trading knowledge retrieved from Chroma. LangGraph routes personal,
general, and mixed questions to specialized retrieval agents before Gemini
generates a grounded answer with citations.

## Core flow

```text
JWT authentication -> RBAC/ownership check -> LangGraph routing
                   -> PostgreSQL trader profile + Chroma knowledge
                   -> hybrid prompt -> Gemini -> answer with sources
```

## Local setup

1. Copy `.env.example` to `.env`, set `GEMINI_API_KEY`, and replace
   `JWT_SECRET_KEY` with a long random value.
2. Start PostgreSQL and provision the schema:

```powershell
docker compose up -d
uv run alembic upgrade head
```

3. Optionally create a demo trader and local users:

```powershell
$env:ALLOW_DEVELOPMENT_BOOTSTRAP="true"
$env:BOOTSTRAP_SAMPLE_TRADER="true"
$env:BOOTSTRAP_TRADER_PASSWORD="change-me"
$env:BOOTSTRAP_ANALYST_PASSWORD="change-me"
$env:BOOTSTRAP_ADMIN_PASSWORD="change-me"
uv run python -m scripts.bootstrap_development_users
```

4. Ingest the PDFs and run the API:

```powershell
uv run python -m scripts.ingest
uv run uvicorn trader_intelligence_ai_copilot.api.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Verification

```powershell
uv run pytest
uv run python -m scripts.verify_trader_repository
uv run python -m scripts.verify_hybrid_chat
```

Use `POST /auth/login` to obtain tokens, then send the access token as
`Authorization: Bearer <token>` to `POST /chat/personalized`.

Useful graph-routing demonstrations:

- `Why am I in Cluster 3?` routes to trader intelligence.
- `What is implied volatility?` routes to generic knowledge.
- `How does my leverage affect my options strategy?` routes to both.

The personalized endpoint returns `403` when a non-admin requests a trader ID
that is not assigned to their account.
