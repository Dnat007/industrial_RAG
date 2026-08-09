import os

from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage

from src.config import FOUNDRY_MODEL_ENDPOINT,FOUNDRY_CHAT_DEPLOYMENT

load_dotenv()

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
)

chat_client = ChatCompletionsClient(
    endpoint=FOUNDRY_MODEL_ENDPOINT,
    credential=credential,
    credential_scopes=[
        "https://cognitiveservices.azure.com/.default"
    ],
)

def generate_answer(messages: list[dict]) -> str:

    chat_messages = []

    for message in messages:

        if message["role"] == "system":

            chat_messages.append(
                SystemMessage(
                    content=message["content"]
                )
            )

        elif message["role"] == "user":

            chat_messages.append(
                UserMessage(
                    content=message["content"]
                )
            )

    response = chat_client.complete(
        messages=chat_messages,
        model=FOUNDRY_CHAT_DEPLOYMENT,
        temperature=0,
    )

    return response.choices[0].message.content
