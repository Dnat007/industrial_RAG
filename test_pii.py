from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from src.config import (
    LANGUAGE_ENDPOINT,
    LANGUAGE_KEY,
)


# =========================================================
# 1. Create Azure Language client
# =========================================================

client = TextAnalyticsClient(
    endpoint=LANGUAGE_ENDPOINT,
    credential=AzureKeyCredential(
        LANGUAGE_KEY
    ),
)


# =========================================================
# 2. Test document
# =========================================================

documents = [
    """
    Employee John Smith can be contacted at
    john.smith@example.com or 9876543210.

    His SSN is 123-45-6789.
    """
]


# =========================================================
# 3. Detect PII
# =========================================================

response = client.recognize_pii_entities(
    documents,
    language="en",
)


# =========================================================
# 4. Display results
# =========================================================

for document in response:

    print("\n" + "=" * 70)
    print("PII DETECTION TEST")
    print("=" * 70)

    print("\nOriginal text:")
    print(documents[0])

    print("\nRedacted text:")
    print(document.redacted_text)

    print("\nDetected entities:")
    print("-" * 70)

    for entity in document.entities:

        print(
            f"Text       : {entity.text}"
        )

        print(
            f"Category   : {entity.category}"
        )

        print(
            f"Confidence : "
            f"{entity.confidence_score:.2f}"
        )

        print("-" * 70)