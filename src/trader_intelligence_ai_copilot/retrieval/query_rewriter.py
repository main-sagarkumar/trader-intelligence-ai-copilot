"""Deterministic conversation-aware retrieval query rewriting."""


class ConversationQueryRewriter:
    """Make ambiguous follow-ups searchable without another LLM call."""

    _FOLLOW_UP_MARKERS = (
        "how can i",
        "what about",
        "explain that",
        "give me",
        "improve",
        "this",
        "that",
        "it",
    )

    @classmethod
    def rewrite(cls, question: str, history: str, trader_id: str) -> str:
        normalized = question.strip().lower()
        is_follow_up = len(question.split()) <= 8 or any(
            marker in normalized for marker in cls._FOLLOW_UP_MARKERS
        )
        if not history.strip() or not is_follow_up:
            return question

        previous_user_lines = [
            line.removeprefix("user: ")
            for line in history.splitlines()
            if line.lower().startswith("user: ")
        ]
        previous = previous_user_lines[-1] if previous_user_lines else history[-500:]
        return f"Trader {trader_id}. Previous question: {previous}. Follow-up: {question}"
