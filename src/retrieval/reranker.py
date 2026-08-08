from azure.search.documents.models import VectorizedQuery

from src.retrieval.hybrid_search import search_client
from src.ingestion.embeddings import embed_documents


def rerank(
    query: str,
    k: int = 5,
    candidate_k: int = 50,
    filter_expression: str | None = None,
):

    query_vector: list[float] = embed_documents([query])[0]

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=candidate_k,
        fields="content_vector",
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],

        filter=filter_expression,

        # Semantic reranking
        query_type="semantic",
        semantic_configuration_name="default",

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

        top=candidate_k,
    )

    return list(results)[:k]