from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from src.config import LANGUAGE_ENDPOINT, LANGUAGE_KEY

client = TextAnalyticsClient(
    endpoint=LANGUAGE_ENDPOINT,
    credential=AzureKeyCredential(
        LANGUAGE_KEY
    ),
)

PROTECTED_CATEGORIES = {

    # Personal information
    "Email",
    "PhoneNumber",
    "Address",

    # Government identifiers
    "USSocialSecurityNumber",
    "PassportNumber",
    "Driver's License Number",

    # Financial information
    "CreditCardNumber",
    "BankAccountNumber",

    # Authentication / security
    "IPAddress",

}


def _is_protected_category(category: str,) -> bool:

    return category in PROTECTED_CATEGORIES


def scan_sensitive_data(text: str) -> dict:

    if not text or not text.strip():
        return {
            "contains_sensitive_data": False,
            "entities": [],
            "redacted_text": text,
        }

    response = client.recognize_pii_entities(
        [text],
        language="en",
    )

    document = response[0]
    entities = []
    protected_entities = []

    for entity in document.entities:
        is_protected = _is_protected_category(entity.category)

        entity_info = {
            "text": entity.text,
            "category": entity.category,
            "confidence": entity.confidence_score,
            "protected": is_protected,
        }

        entities.append(entity_info)

        if is_protected:

            protected_entities.append(entity_info)

    redacted_text = text

    protected_entities_sorted = sorted(
        protected_entities,
        key=lambda x: len(x["text"]),
        reverse=True,
    )

    for entity in protected_entities_sorted:

        sensitive_value = entity["text"]
        replacement = "*" * len(sensitive_value)

        redacted_text = redacted_text.replace(
            sensitive_value,
            replacement,
        )

    return {
        "contains_sensitive_data": (
            len(protected_entities) > 0
        ),

        "entities": entities,
        "protected_entities": protected_entities,
        "redacted_text": redacted_text,
    }
