import json
import re

from src.retrieval.hybrid_search import search_client
from src.generation.llm import generate_answer


# =========================================================
# Query Analyzer
# =========================================================

def _get_relevant_documents(
    query: str,
    max_documents: int = 10,
) -> list[str]:

    """
    Get a lightweight set of documents that appear
    relevant to the user's query.

    This is NOT the final retrieval.

    It is only used to understand whether multiple
    documents/versions could represent different
    interpretations of the query.
    """

    try:

        results = search_client.search(
            search_text=query,
            select=[
                "document_name",
                "document_id",
                "version",
                "effective_date",
                "section",
            ],
            top=max_documents,
        )

        documents = []

        for result in results:

            document_name = result.get(
                "document_name"
            )

            version = result.get(
                "version"
            )

            effective_date = result.get(
                "effective_date"
            )

            section = result.get(
                "section"
            )

            documents.append({
                "document_name": document_name,
                "version": version,
                "effective_date": effective_date,
                "section": section,
            })

        return documents

    except Exception:

        # If lightweight retrieval fails,
        # return an empty catalog.

        return []


# =========================================================
# Extract JSON from LLM response
# =========================================================

def _extract_json(
    text: str,
) -> dict:

    """
    Extract JSON even if the model accidentally
    wraps it in markdown code fences.
    """

    text = text.strip()


    # -----------------------------------------------------
    # Direct JSON
    # -----------------------------------------------------

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        pass


    # -----------------------------------------------------
    # JSON inside ```json ... ```
    # -----------------------------------------------------

    match = re.search(
        r"```json\s*(.*?)\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )


    if match:

        return json.loads(
            match.group(1)
        )


    # -----------------------------------------------------
    # JSON object somewhere inside response
    # -----------------------------------------------------

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL,
    )


    if match:

        return json.loads(
            match.group(0)
        )


    raise ValueError(
        "Query analyzer returned invalid JSON."
    )


# =========================================================
# Analyze Query
# =========================================================

def analyze_query(
    query: str,
) -> dict:

    """
    Generic query ambiguity analyzer.

    Important principle:

    Prefer answering.

    Ask for clarification ONLY when:

    1. Important information is missing
    2. Multiple plausible interpretations exist
    3. Those interpretations could materially
       change the answer

    Broad but answerable questions should NOT
    trigger clarification.
    """


    # =====================================================
    # 1. Find potentially relevant documents
    # =====================================================

    relevant_documents = _get_relevant_documents(
        query=query,
        max_documents=10,
    )


    # =====================================================
    # 2. Build document information
    # =====================================================

    document_information = []

    for document in relevant_documents:

        document_information.append(
            {
                "document_name": document.get(
                    "document_name"
                ),
                "version": document.get(
                    "version"
                ),
                "effective_date": document.get(
                    "effective_date"
                ),
                "section": document.get(
                    "section"
                ),
            }
        )


    # =====================================================
    # 3. Analyzer Prompt
    # =====================================================

    analyzer_prompt = f"""
You are the query-understanding component of an
enterprise RAG system.

Your job is NOT to answer the user's question.

Your job is to decide whether the user's question
needs clarification before retrieval.

USER QUERY:
{query}


POTENTIALLY RELEVANT DOCUMENTS:
{json.dumps(document_information, indent=2)}


IMPORTANT RULES:

1. Prefer answering over asking questions.

2. A broad question is NOT automatically ambiguous.

3. If the user asks:
   "Explain the leave policy"

   and there is one Leave Policy document,
   DO NOT ask which section of the policy they mean.

   The correct decision is:
   is_ambiguous = false

4. If the user asks:
   "Explain company benefits"

   and the documents contain several benefit-related
   sections, answer broadly rather than asking the
   user to select one section.

5. Ask for clarification only when:
   - important information is genuinely missing,
   - multiple plausible interpretations exist,
   - AND choosing between them could materially
     change the answer.

6. If multiple versions/years of the SAME subject exist
   and the user does not specify the year, clarification
   may be necessary.

   Example:
   "Explain pricing"

   If both Pricing2025.pdf and Pricing2026.pdf are
   relevant, ask which year.

7. Do NOT ask unnecessary questions.

8. Do NOT ask about details that do not materially
   affect the answer.

9. If the query can reasonably be answered using the
   available documents, return is_ambiguous=false.

10. Never invent missing information.

11. If clarification is required, ask the minimum number
    of questions necessary.

12. The clarification question must be natural and
    user-friendly.

13. Do not answer the user's original question.

Return ONLY valid JSON.

Required JSON format:

{{
    "is_ambiguous": true,
    "reason": "Short explanation",
    "missing_information": [
        "information that is missing"
    ],
    "clarification_question": "Question to ask the user"
}}

OR:

{{
    "is_ambiguous": false,
    "reason": null,
    "missing_information": [],
    "clarification_question": null
}}
"""


    # =====================================================
    # 4. Ask LLM to analyze
    # =====================================================

    raw_result = generate_answer(
        [
            {
                "role": "system",
                "content": (
                    "You are a strict JSON query "
                    "analysis engine."
                ),
            },
            {
                "role": "user",
                "content": analyzer_prompt,
            },
        ]
    )


    # =====================================================
    # 5. Parse JSON
    # =====================================================

    result = _extract_json(
        raw_result
    )


    # =====================================================
    # 6. Normalize response
    # =====================================================

    is_ambiguous = bool(
        result.get(
            "is_ambiguous",
            False,
        )
    )


    missing_information = result.get(
        "missing_information",
        [],
    )


    clarification_question = result.get(
        "clarification_question"
    )


    # =====================================================
    # 7. Safety rule
    #
    # If analyzer says ambiguous but does not provide
    # a useful clarification question, don't block.
    # =====================================================

    if (
        is_ambiguous
        and not clarification_question
    ):

        is_ambiguous = False

        missing_information = []

        clarification_question = None


    return {
        "is_ambiguous": is_ambiguous,
        "reason": result.get(
            "reason"
        ),
        "missing_information": (
            missing_information
        ),
        "clarification_question": (
            clarification_question
        ),
    }