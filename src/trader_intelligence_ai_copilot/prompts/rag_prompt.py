"""
RAG prompt builder for the Trader Intelligence AI Copilot.
"""

from langchain_core.prompts import ChatPromptTemplate


class RAGPromptBuilder:
    """
    Builds the chat prompt used by the Retrieval-Augmented
    Generation (RAG) pipeline.
    """

    @staticmethod
    def build() -> ChatPromptTemplate:
        """
        Build and return the RAG prompt template.

        Returns
        -------
        ChatPromptTemplate
            Prompt template containing the system and user messages.
        """

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are Trader Intelligence AI Copilot.

Your purpose is to help traders understand:

- Trader Intelligence reports
- Cluster classifications
- Trading concepts
- Risk management
- Recommendations
- Trading psychology

Guidelines:

1. Use ONLY the provided context.
2. Never fabricate information.
3. If the answer is not available in the context,
   clearly state that you do not have enough information.
4. Be clear, concise and professional.
5. When possible, explain concepts in a way that helps
   traders improve their understanding.
""",
                ),
                (
                    "human",
                    """
Context:

{context}

Question:

{question}
""",
                ),
            ]
        )