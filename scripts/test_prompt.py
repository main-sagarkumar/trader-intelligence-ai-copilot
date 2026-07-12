from trader_intelligence_ai_copilot.prompts import RAGPromptBuilder


def main():
    prompt = RAGPromptBuilder.build()

    prompt_value = prompt.invoke(
        {
            "context": "Stop-loss limits downside risk.",
            "question": "Why should I use stop-loss?",
        }
    )

    messages = prompt_value.to_messages()

    print("=" * 80)
    print("SYSTEM MESSAGE")
    print("=" * 80)
    print(messages[0].content)

    print()

    print("=" * 80)
    print("HUMAN MESSAGE")
    print("=" * 80)
    print(messages[1].content)


if __name__ == "__main__":
    main()