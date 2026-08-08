from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from src.config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_INDEX_NAME,
)

from src.ingestion.embeddings import embed_documents

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(
        AZURE_SEARCH_API_KEY
    ),
)

def hybrid_search(
    query: str,
    k: int = 5,
    filter_expression: str | None = None,
):
    query_vector: list[float] = embed_documents([query] )[0]

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=k,
        fields="content_vector",
    )
    # Azure AI Search combines both hybrid and bm25 using RRF.
    results = search_client.search(
        # BM25 / lexical search
        search_text=query,
        # Vector search
        vector_queries=[vector_query],
        # Metadata filtering
        filter=filter_expression,
        # Fields returned from Azure AI Search
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
        # Number of final results
        top=k,
    )

    return list(results)
