from langchain_core.messages import HumanMessage

from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider


class ChatService:

    def __init__(self, llm: BaseLLMProvider):
        self._llm = llm

    async def chat(self, question: str) -> str:

        messages = [
            HumanMessage(content=question)
        ]

        return await self._llm.generate_response(messages)
    