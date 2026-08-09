import json
import re
from src.retrieval.hybrid_search import search_client
from src.generation.llm import generate_answer


def _get_relevant_documents(query, max_documents):
    try:
        results = search_client.search(
            search_text=query,
            select=["document_name", "document_id",
                    "version", "effective_date", "section"],
            top=max_documents,
        )

        documents = []
        for result in results:

            document_name = result.get("document_name")
            version = result.get("version")
            effective_date = result.get("effective_date")
            section = result.get("section")
            documents.append({
                "document_name": document_name,
                "version": version,
                "effective_date": effective_date,
                "section": section,
            })

        return documents
    except Exception:
        return []


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(
        r"```json\s*(.*?)\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return json.loads(match.group(1))

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return json.loads(match.group(0))
    raise ValueError("Query analyzer returned invalid JSON.")


def analyze_query(query: str) -> dict:

    relevant_documents = _get_relevant_documents(
        query=query,
        max_documents=10,
    )

    document_information = []

    for document in relevant_documents:
        document_information.append(
            {
                "document_name": document.get("document_name"),
                "version": document.get("version"),
                "effective_date": document.get("effective_date"),
                "section": document.get("section"),
            }
        )

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

5. Ask for clarification only when:
   - important information is genuinely missing,
   - multiple plausible interpretations exist,
   - AND choosing between them could materially
     change the answer.

6. If multiple versions/years of the SAME subject exist
   and the user does not specify the year, clarification
   may be necessary.

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

    result = _extract_json(
        raw_result
    )

    is_ambiguous = bool(
        result.get(
            "is_ambiguous",
            False,
        )
    )

    missing_information = result.get("missing_information", [])
    clarification_question = result.get("clarification_question")

    if (is_ambiguous and not clarification_question):

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
