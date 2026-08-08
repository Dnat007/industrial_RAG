import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference import EmbeddingsClient

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.storage.blob import BlobServiceClient

load_dotenv()

credential = DefaultAzureCredential()

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=credential
)

project.get_openai_client()

print("Foundry Chat: CONNECTED")


# 2. Foundry Embedding
embedding = EmbeddingsClient(
    endpoint=os.environ["FOUNDRY_MODEL_ENDPOINT"],
    credential=credential,
    model=os.environ["FOUNDRY_EMBEDDING_MODEL"]
)

print("Foundry Embedding: CLIENT CREATED")


# 3. Azure AI Search
search = SearchIndexClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    credential=AzureKeyCredential(
        os.environ["AZURE_SEARCH_API_KEY"]
    )
)

list(search.list_indexes())

print("Azure AI Search: CONNECTED")


# 4. Azure Blob Storage
storage = BlobServiceClient(
    account_url=(
        f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}"
        ".blob.core.windows.net"
    ),
    credential=credential
)

container = storage.get_container_client(
    os.environ["AZURE_STORAGE_CONTAINER_NAME"]
)

container.exists()

print("Azure Blob Storage: CONNECTED")
