from typing import cast

from azure.identity import DefaultAzureCredential
from azure.ai.inference import EmbeddingsClient

from src.config import (
    FOUNDRY_MODEL_ENDPOINT,
    FOUNDRY_EMBEDDING_MODEL,
)


credential = DefaultAzureCredential()

embedding_client = EmbeddingsClient(
    endpoint=FOUNDRY_MODEL_ENDPOINT,
    credential=credential,
    model=FOUNDRY_EMBEDDING_MODEL,
    credential_scopes=[
        "https://cognitiveservices.azure.com/.default"
    ]
)


def embed_documents(texts: list[str]) -> list[list[float]]:

    response = embedding_client.embed(
        input=texts
    )

    return [
        cast(list[float], item.embedding)
        for item in response.data
    ]
