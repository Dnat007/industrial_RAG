from src.retrieval.reranker import rerank
from src.conversation.context import build_context
from src.generation.prompt import build_prompt
from src.generation.llm import generate_answer

from src.security.prompt_shield import shield_prompt
from src.security.guardrails import (
    validate_query,
    validate_output,
)


def ask(
    query: str,
    k: int = 5,
    candidate_k: int = 50,
    allowed_access_levels: list[str] | None = None,
    departments: list[str] | None = None,
    versions: list[str] | None = None,
    document_ids: list[str] | None = None,
) -> dict:

    # =========================================================
    # 1. LOCAL INPUT GUARDRAILS
    # =========================================================

    try:

        validate_query(query)

    except ValueError as e:

        return {
            "answer": str(e),
            "sources": [],
            "blocked": True,
            "block_reason": "input_guardrail",
        }


    # =========================================================
    # 2. USER PROMPT INJECTION CHECK
    # =========================================================

    try:

        user_security = shield_prompt(
            user_prompt=query,
            documents=[],
        )

    except Exception:

        return {
            "answer": (
                "I couldn't securely process your request "
                "because the security validation service "
                "is currently unavailable."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": "security_service_unavailable",
        }


    # ---------------------------------------------------------
    # Block user prompt if injection is detected
    # ---------------------------------------------------------

    if user_security["user_attack"]:

        return {
            "answer": (
                "I can't process this request because "
                "it appears to contain a potentially "
                "unsafe prompt injection."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": "user_prompt_injection",
        }


    # =========================================================
    # 3. HYBRID RETRIEVAL + SEMANTIC RERANKING
    # =========================================================

    results = rerank(
        query=query,
        k=k,
        candidate_k=candidate_k,
        allowed_access_levels=allowed_access_levels,
        departments=departments,
        versions=versions,
        document_ids=document_ids,
    )


    # =========================================================
    # 4. DOCUMENT PROMPT INJECTION CHECK
    # =========================================================

    document_texts = [
        result.get("content", "")
        for result in results
    ]


    try:

        document_security = shield_prompt(
            user_prompt=query,
            documents=document_texts,
        )

    except Exception:

        return {
            "answer": (
                "I couldn't safely validate the retrieved "
                "documents."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": (
                "document_security_validation_failed"
            ),
        }


    # =========================================================
    # 5. REMOVE MALICIOUS DOCUMENT CHUNKS
    # =========================================================

    blocked_indexes = set(
        document_security["document_attacks"]
    )


    safe_results = [
        result
        for index, result in enumerate(results)
        if index not in blocked_indexes
    ]


    # =========================================================
    # 6. CHECK WHETHER SAFE DOCUMENTS REMAIN
    # =========================================================

    if not safe_results:

        return {
            "answer": (
                "I couldn't safely use the retrieved "
                "documents to answer this question."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": (
                "document_prompt_injection"
            ),
        }


    # =========================================================
    # 7. BUILD CONTEXT
    # =========================================================

    context = build_context(
        safe_results
    )


    # =========================================================
    # 8. BUILD LLM PROMPT
    # =========================================================

    messages = build_prompt(
        query=query,
        context=context,
    )


    # =========================================================
    # 9. GENERATE ANSWER
    # =========================================================

    raw_answer = generate_answer(
        messages
    )


    # =========================================================
    # 10. OUTPUT GUARDRAILS
    # =========================================================

    try:

        answer = validate_output(
            raw_answer
        )

    except ValueError:

        return {
            "answer": (
                "I couldn't return the generated response "
                "because it did not pass the required "
                "security checks."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": "output_guardrail",
        }


    # =========================================================
    # 11. SOURCES
    # =========================================================

    sources = []

    for result in safe_results:

        sources.append({
            "document_name": result.get(
                "document_name"
            ),
            "page_number": result.get(
                "page_number"
            ),
            "document_id": result.get(
                "document_id"
            ),
        })

    return {
        "answer": answer,
        "sources": sources,
        "blocked": False,
        "block_reason": None,
    }