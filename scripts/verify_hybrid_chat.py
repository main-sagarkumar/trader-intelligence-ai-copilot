"""Manually verify the real personalized hybrid RAG flow."""

import asyncio

from trader_intelligence_ai_copilot.application import HybridChatService
from trader_intelligence_ai_copilot.chat import HybridContextBuilder
from trader_intelligence_ai_copilot.database.session import SessionLocal, get_engine
from trader_intelligence_ai_copilot.llm.factory import get_llm
from trader_intelligence_ai_copilot.repositories import PostgresTraderRepository
from trader_intelligence_ai_copilot.retrieval.factory import get_retriever

TRADER_ID = "TRADER_101"
QUESTION = "Why am I Cluster 3, and what should I improve?"


async def main() -> None:
    """Retrieve hybrid context and print Gemini's personalized response."""
    with SessionLocal(bind=get_engine()) as session:
        context_builder = HybridContextBuilder(
            trader_repository=PostgresTraderRepository(session),
            retriever=get_retriever(),
        )
        service = HybridChatService(
            llm=get_llm(),
            context_builder=context_builder,
        )
        result = await service.chat(
            question=QUESTION,
            trader_id=TRADER_ID,
        )

    print("Answer:\n")
    print(result.answer)
    print("\nSources:")
    for source in result.sources:
        print(
            f"- {source.document_name} "
            f"(category={source.category}, page={source.page})"
        )


if __name__ == "__main__":
    asyncio.run(main())
