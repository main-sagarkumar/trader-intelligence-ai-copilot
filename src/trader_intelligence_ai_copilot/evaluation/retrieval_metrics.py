"""Information-retrieval metrics for ranked RAG evidence."""

from dataclasses import dataclass
from math import log2


@dataclass(frozen=True, slots=True)
class RetrievalScores:
    precision_at_k: float
    recall_at_k: float
    hit_rate_at_k: float
    reciprocal_rank: float
    ndcg_at_k: float


def score_retrieval(
    ranked_ids: list[str], relevance: dict[str, int], k: int
) -> RetrievalScores:
    """Score a unique ranked document list against graded relevance labels."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    ranked = ranked_ids[:k]
    relevant_ids = {document_id for document_id, grade in relevance.items() if grade > 0}
    hits = [document_id for document_id in ranked if document_id in relevant_ids]
    precision = len(hits) / k
    recall = len(set(hits)) / len(relevant_ids) if relevant_ids else 1.0
    hit_rate = float(bool(hits))

    reciprocal_rank = 0.0
    for rank, document_id in enumerate(ranked, start=1):
        if document_id in relevant_ids:
            reciprocal_rank = 1 / rank
            break

    actual_grades = [relevance.get(document_id, 0) for document_id in ranked]
    ideal_grades = sorted(relevance.values(), reverse=True)[:k]
    dcg = _discounted_gain(actual_grades)
    ideal_dcg = _discounted_gain(ideal_grades)
    ndcg = dcg / ideal_dcg if ideal_dcg else 1.0
    return RetrievalScores(precision, recall, hit_rate, reciprocal_rank, ndcg)


def _discounted_gain(grades: list[int]) -> float:
    return sum(
        ((2**grade) - 1) / log2(rank + 1)
        for rank, grade in enumerate(grades, start=1)
    )
