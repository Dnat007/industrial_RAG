import re

MAX_QUERY_LENGTH = 5000

INJECTION_PATTERNS = [

    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?system\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"override\s+(the\s+)?system\s+prompt",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+system\s+prompt",
    r"print\s+(the\s+)?system\s+prompt",
    r"reveal\s+(all\s+)?hidden\s+instructions",
    r"reveal\s+(all\s+)?developer\s+instructions",
    r"show\s+(me\s+)?your\s+hidden\s+instructions",
    r"ignore\s+your\s+rules",
    r"bypass\s+(your\s+)?security",
    r"bypass\s+(the\s+)?safety",
    r"disable\s+(your\s+)?safety",
    r"jailbreak",
]

def local_injection_check(query: str,) -> bool:
    normalized_query = query.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern,normalized_query):
            return True
    return False

def validate_query(query: str,) -> None:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError("Query is too long.")

    if local_injection_check(query):
        raise ValueError("Potential prompt injection detected.")

MAX_ANSWER_LENGTH = 10000

SYSTEM_PROMPT_PATTERNS = [
    r"system\s+prompt",
    r"system\s+message",
    r"developer\s+message",
    r"developer\s+instructions",
    r"hidden\s+instructions",
    r"internal\s+instructions",
]

SECRET_PATTERNS = [
    # Generic password assignment
    r"password\s*[:=]\s*\S+",

    # Generic API key assignment
    r"api[_\s-]?key\s*[:=]\s*\S+",

    # Generic access token
    r"access[_\s-]?token\s*[:=]\s*\S+",

    # Generic secret assignment
    r"secret\s*[:=]\s*\S+",

    # JWT-like token
    r"eyJ[a-zA-Z0-9_-]{10,}\.",

]

def validate_answer_structure(answer: str,) -> None:

    if not answer or not answer.strip():
        raise ValueError("The model returned an empty response.")

    if len(answer) > MAX_ANSWER_LENGTH:
        raise ValueError(
            "The model response exceeded the "
            "maximum allowed length."
        )

def contains_system_prompt_leak(answer: str) -> bool:

    normalized_answer = answer.lower()

    for pattern in SYSTEM_PROMPT_PATTERNS:

        if re.search(
            pattern,
            normalized_answer,
        ):
            return True

    return False

def contains_secret(answer: str,) -> bool:

    for pattern in SECRET_PATTERNS:
        if re.search(pattern,answer):
            return True

    return False

def validate_output(answer: str,) -> str:

    validate_answer_structure(answer)
    if contains_system_prompt_leak(answer):

        raise ValueError(
            "The model response attempted to "
            "reveal internal instructions."
        )

    if contains_secret(answer):
        raise ValueError(
            "The model response appears to contain "
            "sensitive credentials or secrets."
        )

    return answer