"""Evaluate the live configured retriever against labeled document relevance."""

from pathlib import Path

from trader_intelligence_ai_copilot.evaluation.retrieval_runner import (
    RetrievalEvaluationRunner,
)
from trader_intelligence_ai_copilot.retrieval.factory import get_retriever


def main() -> None:
    cases = RetrievalEvaluationRunner.load_cases(
        Path("data/evaluation/retrieval_cases.json")
    )
    retriever = get_retriever()

    def retrieve(case, k):
        documents = retriever.retrieve(
            case.question,
            k=k,
            metadata_filter={"category": case.category} if case.category else None,
            search_type="mmr",
        )
        return [str(document.metadata.get("document_name", "Unknown")) for document in documents]

    report = RetrievalEvaluationRunner.run(cases, retrieve, k=5)
    print(f"Cases: {report.case_count}")
    for name in report.averages.__dataclass_fields__:
        print(f"{name.replace('_', ' ').title()}: {getattr(report.averages, name):.3f}")


if __name__ == "__main__":
    main()
