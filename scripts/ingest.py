from pathlib import Path

from trader_intelligence_ai_copilot.api.dependencies import (
    get_ingest_service,
)


def main() -> None:

    ingest_service = get_ingest_service()

    ingest_service.ingest(
        Path("data/documents"),
    )


if __name__ == "__main__":
    main()