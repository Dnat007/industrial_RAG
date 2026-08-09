from src.security.sensitive_data import (
    scan_sensitive_data,
)


text = """
Employee John Smith works in the HR department.

His email is john.smith@example.com
and his phone number is 9876543210.

His SSN is 123-45-6789.
"""


result = scan_sensitive_data(
    text
)


print("\n" + "=" * 70)
print("SENSITIVE DATA TEST")
print("=" * 70)


print("\nOriginal:")
print(text)


print("\nRedacted:")
print(
    result["redacted_text"]
)

print("\nDetected entities:")
print("-" * 70)


for entity in result["entities"]:

    print(
        f"Text       : {entity['text']}"
    )

    print(
        f"Category   : {entity['category']}"
    )

    print(
        f"Confidence : "
        f"{entity['confidence']:.2f}"
    )

    print(
        f"Protected  : "
        f"{entity['protected']}"
    )

    print("-" * 70)