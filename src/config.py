import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing environment variable: {name}")

    return value


# Microsoft Foundry
FOUNDRY_PROJECT_ENDPOINT = get_env("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_CHAT_DEPLOYMENT = get_env("FOUNDRY_CHAT_DEPLOYMENT")

FOUNDRY_MODEL_ENDPOINT = get_env("FOUNDRY_MODEL_ENDPOINT")
FOUNDRY_EMBEDDING_MODEL = get_env("FOUNDRY_EMBEDDING_MODEL")


# Azure AI Search
AZURE_SEARCH_ENDPOINT = get_env("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = get_env("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = get_env("AZURE_SEARCH_INDEX_NAME")


# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME = get_env(
    "AZURE_STORAGE_ACCOUNT_NAME"
)

AZURE_STORAGE_CONTAINER_NAME = get_env(
    "AZURE_STORAGE_CONTAINER_NAME"
)