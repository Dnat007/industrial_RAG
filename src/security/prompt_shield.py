import requests
from src.config import (
    CONTENT_SAFETY_ENDPOINT,
    CONTENT_SAFETY_KEY,
)

API_VERSION = "2024-09-01"

class PromptInjectionDetected(Exception):
    """
    Raised when Azure Prompt Shields detects a potential prompt injection attack.
    """
    pass

def shield_prompt(
    user_prompt: str,
    documents: list[str] | None = None,
) -> dict:

    endpoint = CONTENT_SAFETY_ENDPOINT.rstrip("/")

    url = (
        f"{endpoint}"
        f"/contentsafety/text:shieldPrompt"
        f"?api-version={API_VERSION}"
    )

    headers = {
        "Ocp-Apim-Subscription-Key": (
            CONTENT_SAFETY_KEY
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "userPrompt": user_prompt,
        "documents": documents or [],
    }

    response = requests.post(url,headers=headers,json=payload,timeout=10)

    response.raise_for_status()

    result = response.json()

    user_attack = result.get(
        "userPromptAnalysis",
        {}
    ).get(
        "attackDetected",
        False,
    )

    document_attacks = []
    document_results = result.get("documentsAnalysis",[])

    for index, analysis in enumerate(document_results):

        if analysis.get("attackDetected",False):
            document_attacks.append(index)

    safe = (
        not user_attack
        and not document_attacks
    )

    return {
        "user_attack": user_attack,
        "document_attacks": document_attacks,
        "safe": safe,
    }

def validate_user_prompt(user_prompt: str) -> None:

    result = shield_prompt(user_prompt=user_prompt, documents=[],)

    if result["user_attack"]:
        raise PromptInjectionDetected(
            "Potential prompt injection attack "
            "detected in user input."
        )