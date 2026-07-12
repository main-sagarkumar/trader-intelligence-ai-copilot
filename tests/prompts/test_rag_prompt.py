from langchain_core.prompts import ChatPromptTemplate
import pytest

from trader_intelligence_ai_copilot.prompts import RAGPromptBuilder


def test_build_returns_chat_prompt_template():
    """RAGPromptBuilder should return a ChatPromptTemplate."""

    prompt = RAGPromptBuilder.build()

    assert isinstance(prompt, ChatPromptTemplate)


def test_prompt_contains_system_and_human_messages():
    """Prompt should generate exactly one system and one human message."""

    prompt = RAGPromptBuilder.build()

    prompt_value = prompt.invoke(
        {
            "context": "Stop-loss limits downside risk.",
            "question": "Why should I use stop-loss?",
        }
    )

    messages = prompt_value.to_messages()

    assert len(messages) == 2

    assert messages[0].type == "system"
    assert messages[1].type == "human"


def test_prompt_injects_context_and_question():
    """Context and question should appear in the human message."""

    context = "Stop-loss limits downside risk."
    question = "Why should I use stop-loss?"

    prompt = RAGPromptBuilder.build()

    prompt_value = prompt.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    messages = prompt_value.to_messages()

    assert context in messages[1].content
    assert question in messages[1].content


def test_prompt_requires_all_variables():
    """Prompt should fail if required variables are missing."""

    prompt = RAGPromptBuilder.build()

    with pytest.raises(Exception):
        prompt.invoke(
            {
                "context": "Some context"
            }
        )

def test_system_prompt_contains_grounding_instructions():
    """System prompt should instruct the model to use only provided context."""

    prompt = RAGPromptBuilder.build()

    prompt_value = prompt.invoke(
        {
            "context": "Context",
            "question": "Question",
        }
    )

    messages = prompt_value.to_messages()

    system_prompt = messages[0].content

    assert "Use ONLY the provided context" in system_prompt
    assert "Never fabricate information" in system_prompt
    assert "do not have enough information" in system_prompt
    assert "Be clear, concise and professional" in system_prompt