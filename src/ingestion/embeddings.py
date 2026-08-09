import os
from typing import cast
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.inference import EmbeddingsClient
from src.config import FOUNDRY_MODEL_ENDPOINT,FOUNDRY_EMBEDDING_MODEL


load_dotenv()

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
)

embedding_client = EmbeddingsClient(
    endpoint=FOUNDRY_MODEL_ENDPOINT,
    credential=credential,
    model=FOUNDRY_EMBEDDING_MODEL,
    credential_scopes=[
        "https://cognitiveservices.azure.com/.default"
    ],
)

def embed_documents(texts: list[str]) -> list[list[float]]:

    response = embedding_client.embed(
        input=texts
    )

    return [
        cast(list[float], item.embedding)
        for item in response.data
    ]
