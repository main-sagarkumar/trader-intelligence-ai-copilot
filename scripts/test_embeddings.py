from trader_intelligence_ai_copilot.embeddings.factory import get_embedding_provider

embedding_model = get_embedding_provider()

vector = embedding_model.embed_query(
    "What is risk management?"
)

print(f"Embedding dimension: {len(vector)}")