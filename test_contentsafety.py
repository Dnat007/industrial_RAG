from src.config import (
    CONTENT_SAFETY_ENDPOINT,
    CONTENT_SAFETY_KEY,
)


print("Content Safety configuration loaded.")

print(
    "Endpoint:",
    CONTENT_SAFETY_ENDPOINT
)

print(
    "Key loaded:",
    bool(CONTENT_SAFETY_KEY)
)