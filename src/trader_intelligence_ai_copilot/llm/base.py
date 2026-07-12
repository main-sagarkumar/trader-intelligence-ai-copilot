from abc import ABC, abstractmethod
from collections.abc import Sequence

from langchain_core.messages import BaseMessage


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    async def generate_response(
        self,
        messages: Sequence[BaseMessage],
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError