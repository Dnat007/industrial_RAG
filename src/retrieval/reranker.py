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
   
    query_vector: list[float] = embed_documents([query])[0]

    filter_expression = build_filter(
        allowed_access_levels=allowed_access_levels,
        departments=departments,
        versions=versions,
        document_ids=document_ids,
    )

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=candidate_k,
        fields="content_vector",
    )

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
    final_results = results[:k]

    return final_results