from src.retrieval.reranker import rerank
from src.conversation.context import build_context


query = "What is the leave policy?"


results = rerank(
    query=query,
    k=5,
    candidate_k=50,
    allowed_access_levels=["internal"],
)


context = build_context(results)


print("\n")
print("=" * 70)
print("GENERATED CONTEXT")
print("=" * 70)
print()

print(context)