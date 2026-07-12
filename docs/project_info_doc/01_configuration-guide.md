# Configuration guide

This document explains the configuration code in `src/trader_intelligence_ai_copilot/config` in beginner-friendly terms.

## What this package does

The configuration package keeps values that may change between environments out of the Python application code. Examples include the application name, database connection URL, API keys, and the language-model choice.

It reads these values from environment variables. During local development, those variables can be stored in a `.env` file. `.env.example` is the safe template to copy; the real `.env` file must not be committed because it can contain secrets.

## Flow

```mermaid
flowchart TD
    A[Defaults defined in Python] --> C[Configuration class]
    B[OS environment variables or .env file] --> C
    C --> D[ApplicationSettings]
    D --> E[get_settings cached singleton]
    E --> F[FastAPI application]
    E --> G[Health endpoint]
    E --> H[Future database, LLM, and security services]
```

When a configuration value is loaded, an environment variable wins over the default in the Python code. For example, `DEBUG=True` in `.env` overrides the `False` default in `ApplicationConfig`.

## Package structure

| Location | Responsibility |
| --- | --- |
| `base.py` | Shared rules for loading settings from `.env` and environment variables. |
| `app/` | Application-facing settings: identity, logs, and security. |
| `infra/` | Infrastructure settings: database, credentials, and LLM. |
| `enums/` | Allowed fixed choices, such as `development` or `gemini`. |
| `settings.py` | Builds one grouped settings object for the application. |
| `__init__.py` | Provides the public imports: `ApplicationSettings` and `get_settings`. |

## How the pieces work

### 1. `BaseConfig`: the common loader

Every real configuration class inherits from `BaseConfig`.

```python
class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

In plain language:

- `env_file=".env"` tells Pydantic to read the local `.env` file.
- `case_sensitive=False` means environment-variable names are not case-sensitive while loading.
- `extra="ignore"` allows `.env` to contain variables that a particular configuration class does not use.

Each child class can therefore focus only on the values it owns.

### 2. App settings (`app/`)

`ApplicationConfig` controls basic application identity and mode:

- `APP_NAME`: defaults to `Trader Intelligence AI Copilot`.
- `APP_VERSION`: defaults to `0.1.0`.
- `ENVIRONMENT`: one of `development`, `testing`, or `production`; defaults to `development`.
- `DEBUG`: a boolean flag; defaults to `False`.

`LoggingConfig` contains `LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`) and `JSON_LOGS`. `SecurityConfig` contains the JWT signing key, signing algorithm, and token lifetime.

The running FastAPI app already reads `settings.app.name` and `settings.app.version` to set its title and version. The health route uses the same settings, so both locations report the same application identity.

### 3. Infrastructure settings (`infra/`)

`DatabaseConfig` contains:

- `DATABASE_PROVIDER`: `postgres`, `mysql`, or `sqlite`; defaults to `postgres`.
- `DATABASE_URL`: the secret connection string.
- `DATABASE_ECHO`: whether database SQL should be logged.
- `DATABASE_POOL_SIZE`: maximum baseline number of reusable connections.

`CredentialsConfig` stores `GEMINI_API_KEY` and `OPENAI_API_KEY` as `SecretStr`. `SecretStr` is useful because its normal printed representation hides the value, reducing accidental exposure in logs.

`LLMConfig` selects the language-model provider and model, plus generation controls:

- `LLM_PROVIDER`: `gemini`, `openai`, `claude`, or `azure_openai`; defaults to `gemini`.
- `LLM_MODEL`: defaults to `gemini-2.5-flash`.
- `LLM_TEMPERATURE`: controls how varied model output can be; `0.2` is relatively consistent.
- `LLM_MAX_TOKENS`: response-size limit; defaults to `2048`.
- `LLM_TIMEOUT`: wait limit in seconds; defaults to `60`.

### 4. Enums: restricting choices

An enum is a named, limited list of allowed values. It catches mistakes early. For example, `ENVIRONMENT=devlopment` is rejected because the valid value is `development`.

Provider enums define the currently supported choices for databases, LLMs, embeddings, and vector stores.

### 5. `ApplicationSettings`: one configuration object

`settings.py` gathers the active configuration sections:

```python
settings = get_settings()

print(settings.app.name)
print(settings.database.provider)
print(settings.llm.model)
```

`get_settings()` uses `@lru_cache`. The first call creates `ApplicationSettings`; later calls reuse that same instance. This avoids repeatedly reading and validating settings during one application process.

Use it at module or application boundaries, then pass only the values a service needs. Do not repeatedly construct `ApplicationSettings()` in request handlers.

## Local setup example

1. Copy `.env.example` to `.env`.
2. Keep safe defaults for ordinary local development.
3. Add secret values only to `.env` (or to the deployment platform's secret store).

Example:

```dotenv
APP_NAME=Trader Intelligence AI Copilot
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

DATABASE_PROVIDER=postgres
DATABASE_URL=postgresql://user:password@localhost:5432/trader_copilot

LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GEMINI_API_KEY=replace-with-your-local-secret
```

Never paste a real database password, JWT key, or API key into source code, documentation, or `.env.example`.

## Current implementation status

The following files are intentional placeholders at the moment and do not yet define configuration classes:

- `infra/embeddings.py`
- `infra/vectorstore.py`
- `infra/monitoring.py`

`.env.example` already includes `EMBEDDING_PROVIDER` and `VECTORSTORE_PROVIDER`, but `ApplicationSettings` does not load them yet. `DATABASE_MAX_OVERFLOW` is also present in the template but is not yet a field on `DatabaseConfig`. This is safe today because `BaseConfig` ignores extra variables; it simply means those values have no effect until their matching settings are implemented.

## Adding a new setting

To add an application setting, add a field to the right class and give it an environment-variable alias:

```python
from pydantic import Field

class ApplicationConfig(BaseConfig):
    request_timeout_seconds: int = Field(
        default=30,
        alias="REQUEST_TIMEOUT_SECONDS",
    )
```

Then add `REQUEST_TIMEOUT_SECONDS=30` to `.env.example`, document it, and access it as `get_settings().app.request_timeout_seconds`. For a new group such as monitoring, create a `MonitoringConfig` class and add it to `ApplicationSettings`.
