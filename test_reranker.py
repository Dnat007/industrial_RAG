from src.retrieval.reranker import rerank


query = "What is the leave policy?"


results = rerank(
    query=query,
    candidate_k=50,
    k=5,
)


print("\n" + "=" * 70)
print("HYBRID SEARCH + SEMANTIC RANKER")
print("=" * 70)


for i, result in enumerate(results, 1):

    print(f"\nResult {i}")
    print("-" * 50)

    print(
        "Document:",
        result.get("document_name")
    )

    print(
        "Page:",
        result.get("page_number")
    )

    print(
        "Search Score:",
        result.get("@search.score")
    )

    print(
        "Reranker Score:",
        result.get("@search.reranker_score")
    )

    print(
        "Content:",
        result.get("content", "")[:500]
    )