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

## Conversation memory

The first personalized request may omit `session_id`; the response returns a
new UUID. Send that UUID on follow-up requests to include the eight most recent
messages. Sessions are bound to both the authenticated user and trader profile,
so another user cannot resume them.

## Intelligent retrieval

Specialized agents apply category filters and Chroma MMR search to retrieve
diverse evidence. Ambiguous follow-ups are rewritten deterministically from the
latest user turn before retrieval, while the original wording remains in the
prompt. Context and citations are deduplicated by document path and page.

## AI safety and PII

Input guardrails block prompt-injection attempts and convert guaranteed-profit
or definitive trade requests into an educational safety response. PII is
redacted before retrieval, model calls, and conversation persistence, including
email, Indian phone, Aadhaar, PAN, and payment-card patterns. Output guardrails
scan for PII, credentials, database URLs, cross-trader identifiers, and answers
without retrieved evidence.

## Offline evaluation gate

The golden dataset covers routing, retrieval categories, guardrail behavior,
PII redaction, and trader authorization without calling an external model.

```powershell
uv run python -m scripts.evaluate
```

The command prints metric percentages and exits non-zero on any regression.

## Observability

Every HTTP response includes `X-Request-ID`; callers may provide their own ID
for correlation. Privacy-safe structured events record routes, categories,
document counts, guardrail reasons, and stage latency without questions,
answers, prompts, trader metrics, tokens, or PII. `GET /ready` checks required
configuration, PostgreSQL, and Chroma initialization without calling Gemini.
