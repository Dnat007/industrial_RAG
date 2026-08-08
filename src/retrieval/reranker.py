import time

from azure.search.documents.models import VectorizedQuery

from src.ingestion.embeddings import embed_documents
from src.retrieval.filters import build_filter
from src.retrieval.hybrid_search import search_client


def rerank(
    query: str,
    k: int = 5,
    candidate_k: int = 50,
    allowed_access_levels: list[str] | None = None,
    departments: list[str] | None = None,
    versions: list[str] | None = None,
    document_ids: list[str] | None = None,
):
   
    # embedding_start = time.perf_counter()
    query_vector: list[float] = embed_documents([query])[0]

    # embedding_time = (time.perf_counter() - embedding_start)

    # filter_start = time.perf_counter()
    filter_expression = build_filter(
        allowed_access_levels=allowed_access_levels,
        departments=departments,
        versions=versions,
        document_ids=document_ids,
    )
    # filter_time = (time.perf_counter() - filter_start)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=candidate_k,
        fields="content_vector",
    )

    # search_start = time.perf_counter()

    results = search_client.search(
        search_text=query,
        vector_queries=[
            vector_query
        ],
        filter=filter_expression,
        query_type="semantic",
        semantic_configuration_name="default",
        top=candidate_k,
        select=[
            "id",
            "content",
            "document_name",
            "page_number",
            "document_id",
            "section",
            "department",
            "version",
            "effective_date",
            "access_level",
        ],
    )

    results = list(results)
    # search_time = ( time.perf_counter() - search_start)
    final_results = results[:k]
    # total_retrieval_time = (embedding_time+ filter_time+ search_time)

    # print("\n" + "=" * 60)
    # print("RETRIEVAL LATENCY")
    # print("=" * 60)
    # print(
    #     f"Query Embedding : {embedding_time:.2f} sec"# )
    # print(
    #     f"Filter Building : {filter_time:.4f} sec"# )
    # print(
    #     f"Azure Search    : {search_time:.2f} sec)
    # print(
    #     f"Total Retrieval : {total_retrieval_time:.2f} sec")
    # print("=" * 60)


    return final_results