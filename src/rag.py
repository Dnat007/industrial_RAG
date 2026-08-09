from src.retrieval.reranker import rerank
from src.conversation.context import build_context
from src.generation.prompt import build_prompt
from src.generation.llm import generate_answer

from src.security.prompt_shield import shield_prompt

from src.security.guardrails import (
    validate_query,
    validate_output,
)

from src.security.sensitive_data import (
    scan_sensitive_data,
)

from src.analyzer.analyzer import (
    analyze_query,
)


def ask(
    query: str,
    k: int = 5,
    candidate_k: int = 50,
    allowed_access_levels: list[str] | None = None,
    departments: list[str] | None = None,
    versions: list[str] | None = None,
    document_ids: list[str] | None = None,
    skip_analysis: bool = False,
) -> dict:

    # =========================================================
    # 1. LOCAL INPUT GUARDRAILS
    # =========================================================

    try:

        validate_query(
            query
        )

    except ValueError as e:

        return {
            "answer": str(e),
            "sources": [],
            "blocked": True,
            "block_reason": "input_guardrail",
        }

    # =========================================================
    # 2. QUERY AMBIGUITY ANALYSIS
    # =========================================================

    if not skip_analysis:

        try:

            query_analysis = analyze_query(
                query
            )

        except Exception:

            # If analyzer fails, do not make the
            # entire RAG system unusable.
            #
            # We fall back to normal retrieval.

            query_analysis = {
                "is_ambiguous": False,
                "reason": None,
                "missing_information": [],
                "clarification_question": None,
            }

        # -----------------------------------------------------
        # Ask clarification only for MATERIAL ambiguity
        # -----------------------------------------------------

        if query_analysis[
            "is_ambiguous"
        ]:

            return {
                "answer": (
                    query_analysis[
                        "clarification_question"
                    ]
                ),

                "sources": [],

                "blocked": False,

                "needs_clarification": True,

                "clarification": {
                    "original_query": query,

                    "missing_information": (
                        query_analysis[
                            "missing_information"
                        ]
                    ),

                    "reason": (
                        query_analysis[
                            "reason"
                        ]
                    ),
                },
            }

    # =========================================================
    # 3. USER PROMPT INJECTION CHECK
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
            "block_reason": (
                "security_service_unavailable"
            ),
        }

    if user_security["user_attack"]:

        return {
            "answer": (
                "I can't process this request because "
                "it appears to contain a potentially "
                "unsafe prompt injection."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": (
                "user_prompt_injection"
            ),
        }

    # =========================================================
    # 4. HYBRID RETRIEVAL + SEMANTIC RERANKING
    # =========================================================

    results = rerank(
        query=query,
        k=k,
        candidate_k=candidate_k,

        allowed_access_levels=(
            allowed_access_levels
        ),

        departments=departments,

        versions=versions,

        document_ids=document_ids,
    )

    # =========================================================
    # 5. DOCUMENT PROMPT INJECTION CHECK
    # =========================================================

    document_texts = [
        result.get(
            "content",
            ""
        )
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
                "I couldn't safely validate the "
                "retrieved documents."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": (
                "document_security_validation_failed"
            ),
        }

    # =========================================================
    # 6. REMOVE MALICIOUS DOCUMENT CHUNKS
    # =========================================================

    blocked_indexes = set(
        document_security[
            "document_attacks"
        ]
    )

    safe_results = [
        result
        for index, result in enumerate(results)
        if index not in blocked_indexes
    ]

    # =========================================================
    # 7. NO SAFE DOCUMENTS
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
    # 8. BUILD CONTEXT
    # =========================================================

    context = build_context(
        safe_results
    )

    # =========================================================
    # 9. BUILD LLM PROMPT
    # =========================================================

    messages = build_prompt(
        query=query,
        context=context,
    )

    # =========================================================
    # 10. GENERATE ANSWER
    # =========================================================

    raw_answer = generate_answer(
        messages
    )

    # =========================================================
    # 11. OUTPUT GUARDRAILS
    # =========================================================

    try:

        answer = validate_output(
            raw_answer
        )

    except ValueError:

        return {
            "answer": (
                "I couldn't return the generated "
                "response because it did not pass "
                "the required security checks."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": (
                "output_guardrail"
            ),
        }

    # =========================================================
    # 12. SENSITIVE DATA PROTECTION
    # =========================================================

    try:

        sensitive_result = scan_sensitive_data(
            answer
        )

    except Exception:

        return {
            "answer": (
                "I couldn't safely validate the "
                "generated response for sensitive data."
            ),
            "sources": [],
            "blocked": True,
            "block_reason": (
                "sensitive_data_service_unavailable"
            ),
        }

    # =========================================================
    # 13. REDACT PROTECTED DATA
    # =========================================================

    if sensitive_result[
        "contains_sensitive_data"
    ]:

        answer = sensitive_result[
            "redacted_text"
        ]

    # =========================================================
    # 14. SOURCES
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

    # =========================================================
    # 15. FINAL RESPONSE
    # =========================================================

    return {
        "answer": answer,
        "sources": sources,
        "blocked": False,
        "block_reason": None,
        "needs_clarification": False,
    }
