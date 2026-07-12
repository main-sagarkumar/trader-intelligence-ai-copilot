"""Opt-in LangSmith experiments using sanitized recorded predictions only."""

from typing import Any

from trader_intelligence_ai_copilot.evaluation.answer_quality import (
    AnswerCase,
    AnswerQualityEvaluator,
)


class LangSmithEvaluationAdapter:
    DATASET_NAME = "tiac-sanitized-answer-quality"

    @classmethod
    def examples(cls, cases: list[AnswerCase]) -> list[dict[str, Any]]:
        return [
            {
                "inputs": {"case_id": case.id, "question": case.question},
                "outputs": {
                    "expected_facts": case.expected_facts,
                    "expected_sources": list(case.expected_sources),
                    "forbidden_claims": list(case.forbidden_claims),
                    "required_policy_terms": list(case.required_policy_terms),
                },
            }
            for case in cases
        ]

    @classmethod
    def run(cls, client: Any, cases: list[AnswerCase]) -> Any:
        """Upload sanitized cases and run code-only evaluators in LangSmith."""
        if not client.has_dataset(dataset_name=cls.DATASET_NAME):
            client.create_dataset(
                cls.DATASET_NAME,
                description="Sanitized TIAC answer-quality predictions",
            )
            client.create_examples(
                dataset_name=cls.DATASET_NAME,
                examples=cls.examples(cases),
            )

        predictions = {case.id: case for case in cases}

        def target(inputs: dict[str, Any]) -> dict[str, Any]:
            case = predictions[inputs["case_id"]]
            return {
                "answer": case.answer,
                "sources": list(case.sources),
                "detected_pii": list(case.detected_pii),
                "latency_ms": case.latency_ms,
                "model_version": case.model_version,
                "prompt_version": case.prompt_version,
            }

        return client.evaluate(
            target,
            data=cls.DATASET_NAME,
            evaluators=[cls.deterministic_evaluator],
            experiment_prefix="tiac-answer-quality",
            metadata={"privacy": "sanitized", "agent_count": 2},
        )

    @staticmethod
    def deterministic_evaluator(
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        reference_outputs: dict[str, Any],
    ) -> dict[str, Any]:
        case = AnswerCase(
            id=str(inputs["case_id"]),
            question=str(inputs["question"]),
            answer=str(outputs["answer"]),
            sources=tuple(outputs.get("sources", ())),
            expected_facts=dict(reference_outputs.get("expected_facts", {})),
            expected_sources=tuple(reference_outputs.get("expected_sources", ())),
            forbidden_claims=tuple(reference_outputs.get("forbidden_claims", ())),
            required_policy_terms=tuple(
                reference_outputs.get("required_policy_terms", ())
            ),
            detected_pii=tuple(outputs.get("detected_pii", ())),
        )
        scores = AnswerQualityEvaluator.evaluate_case(case)
        values = [getattr(scores, name) for name in scores.__dataclass_fields__]
        return {"key": "deterministic_quality", "score": sum(values) / len(values)}
