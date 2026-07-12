"""LLM-judge metrics for groundedness, relevance, and faithfulness."""

import json
import re
from dataclasses import dataclass, fields

from langchain_core.messages import HumanMessage, SystemMessage

from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerCase
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider


@dataclass(frozen=True, slots=True)
class SemanticScores:
    groundedness: float
    hallucination_rate: float
    answer_relevance: float
    faithfulness: float


@dataclass(frozen=True, slots=True)
class SemanticReport:
    case_count: int
    averages: SemanticScores
    per_case: dict[str, SemanticScores]


class SemanticJudge:
    """Score sanitized predictions against sanitized permitted evidence."""

    def __init__(self, llm: BaseLLMProvider) -> None:
        self._llm = llm

    async def evaluate_case(self, case: AnswerCase) -> SemanticScores:
        payload = {
            "question": case.question,
            "answer": case.answer,
            "retrieved_contexts": list(case.retrieved_contexts),
            "permitted_trader_facts": case.trader_facts,
            "reference_answer": case.reference_answer,
        }
        response = await self._llm.generate_response(
            [
                SystemMessage(
                    content=(
                        "You are a strict RAG evaluator. Score from 0 to 1. "
                        "Groundedness: claims supported by retrieved contexts or permitted "
                        "trader facts. Answer relevance: directly answers the question. "
                        "Faithfulness: claims supported specifically by retrieved contexts; "
                        "do not reward unsupported additions. Return JSON only with keys "
                        "groundedness, answer_relevance, faithfulness."
                    )
                ),
                HumanMessage(content=json.dumps(payload, ensure_ascii=True)),
            ]
        )
        scores = self._parse_scores(response)
        groundedness = scores["groundedness"]
        return SemanticScores(
            groundedness=groundedness,
            hallucination_rate=1 - groundedness,
            answer_relevance=scores["answer_relevance"],
            faithfulness=scores["faithfulness"],
        )

    async def run(self, cases: list[AnswerCase]) -> SemanticReport:
        if not cases:
            raise ValueError("At least one semantic evaluation case is required.")
        per_case = {case.id: await self.evaluate_case(case) for case in cases}
        count = len(per_case)
        averages = SemanticScores(
            **{
                field.name: sum(
                    getattr(scores, field.name) for scores in per_case.values()
                )
                / count
                for field in fields(SemanticScores)
            }
        )
        return SemanticReport(count, averages, per_case)

    @staticmethod
    def _parse_scores(response: str) -> dict[str, float]:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match is None:
            raise ValueError("Semantic judge did not return a JSON object.")
        payload = json.loads(match.group(0))
        required = ("groundedness", "answer_relevance", "faithfulness")
        scores = {name: float(payload[name]) for name in required}
        if any(score < 0 or score > 1 for score in scores.values()):
            raise ValueError("Semantic judge scores must be between 0 and 1.")
        return scores
