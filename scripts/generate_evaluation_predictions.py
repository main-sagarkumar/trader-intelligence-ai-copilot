"""Generate sanitized evaluation predictions through the fixed two-node graph."""

import asyncio
from pathlib import Path

from trader_intelligence_ai_copilot.agents import (
    GenericKnowledgeAgent,
    TraderIntelligenceAgent,
)
from trader_intelligence_ai_copilot.application import GraphChatService
from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.database.session import SessionLocal, get_engine
from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerQualityEvaluator
from trader_intelligence_ai_copilot.evaluation.prediction_runner import PredictionRunner
from trader_intelligence_ai_copilot.llm.factory import get_llm
from trader_intelligence_ai_copilot.orchestration import TraderGraph
from trader_intelligence_ai_copilot.repositories import PostgresTraderRepository
from trader_intelligence_ai_copilot.retrieval.factory import get_retriever


async def main() -> None:
    cases = AnswerQualityEvaluator.load_cases(
        Path("data/evaluation/answer_cases.json")
    )
    settings = get_settings()
    with SessionLocal(bind=get_engine()) as session:
        retriever = get_retriever()
        service = GraphChatService(
            graph=TraderGraph(
                trader_agent=TraderIntelligenceAgent(
                    PostgresTraderRepository(session), retriever
                ),
                generic_agent=GenericKnowledgeAgent(retriever),
            ),
            llm=get_llm(),
        )

        async def target(case):
            result = await service.chat(case.question, "TRADER_101")
            return result.answer, [source.document_name for source in result.sources]

        predictions = await PredictionRunner.run(
            cases,
            target,
            model_version=settings.llm.model,
            prompt_version="hybrid-rag-v1",
        )

    output = Path("output/evaluation/gemini-predictions.json")
    PredictionRunner.write(predictions, output)
    print(f"Wrote {len(predictions)} sanitized predictions to {output}")


if __name__ == "__main__":
    asyncio.run(main())
