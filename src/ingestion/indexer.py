from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (SearchIndex, SearchField, SearchFieldDataType, SearchableField,
                                                   SemanticConfiguration, SemanticPrioritizedFields, SemanticField, SemanticSearch,
                                                   SimpleField, VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile)

from src.config import (AZURE_SEARCH_ENDPOINT,
                        AZURE_SEARCH_API_KEY, AZURE_SEARCH_INDEX_NAME)

credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)


def create_index():

    index_client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=credential,
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="document_id",
                    type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),

        # Embedding vector
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="vector-profile",
                    ),

        SearchableField(name="document_name",
                        type=SearchFieldDataType.String, filterable=True),

        SimpleField(name="page_number",
                    type=SearchFieldDataType.Int32, filterable=True),
        SearchableField(
            name="section", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="department",
                        type=SearchFieldDataType.String, filterable=True),

        # Version
        SearchableField(
            name="version", type=SearchFieldDataType.String, filterable=True),
        # Effective date
        SimpleField(name="effective_date", type=SearchFieldDataType.DateTimeOffset,
                    filterable=True, sortable=True),
        # Access control
        SearchableField(name="access_level",
                        type=SearchFieldDataType.String, filterable=True),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algorithm")],
        profiles=[
            VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-algorithm")],
    )

    semantic_config = SemanticConfiguration(name="default",
                                            prioritized_fields=SemanticPrioritizedFields(
                                                title_field=SemanticField(
                                                    field_name="document_name"),
                                                content_fields=[SemanticField(field_name="content")]),
                                            )

    semantic_search = SemanticSearch(
        default_configuration_name="default", configurations=[semantic_config])

    index = SearchIndex(name=AZURE_SEARCH_INDEX_NAME, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)

    index_client.create_or_update_index(index)

    print(f"Index '{AZURE_SEARCH_INDEX_NAME}' created successfully.")


def upload_documents(documents):
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=credential,
    )

    result = search_client.upload_documents(documents=documents)
    print(f"Uploaded {len(result)} documents.")


if __name__ == "__main__":
    create_index()
