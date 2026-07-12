from langchain_core.messages import AIMessage


def extract_text(message: AIMessage) -> str:
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    return str(content)