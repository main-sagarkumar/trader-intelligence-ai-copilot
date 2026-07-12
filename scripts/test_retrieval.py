from trader_intelligence_ai_copilot.retrieval.factory import (
    get_retriever,
)


def main():

    retriever = get_retriever()

    results = retriever.retrieve(
        "How can I reduce trading risk?",
        k=3,
    )

    for i, document in enumerate(results, start=1):

        print("=" * 80)

        print(f"Result {i}")

        print(document.metadata)

        print()

        print(document.page_content[:600])


if __name__ == "__main__":
    main()