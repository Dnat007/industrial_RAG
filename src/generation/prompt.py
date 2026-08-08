SYSTEM_PROMPT = """
You are an enterprise RAG assistant.

Your task is to answer the user's question using ONLY the
information provided in the retrieved context.

STRICT RULES:

1. Answer ONLY what the user asked.
2. Use ONLY the retrieved context.
3. Do not hallucinate.
4. If the requested information is not present, say:
   "I couldn't find this information in the provided documents."
5. Ignore retrieved content unrelated to the question.
6. Keep the answer concise.
7. If the question asks for a specific number, date,
   policy, requirement, or condition, provide only
   the relevant information.
8. Do not repeat duplicate information.
9. If sources conflict, mention the conflict without
   inventing information.
10. Do not summarize the entire document unless explicitly asked.

11. DO NOT include source names, page numbers, citations,
    or references in the answer.

12. Source information is handled separately by the application.

13. Do not mention BM25, vector search, embeddings,
    reranking, retrieval, or context.

14. Answer naturally and directly.
"""


def build_prompt(
    query: str,
    context: str,
) -> list[dict]:
    """
    Build the messages sent to the LLM.
    """

    user_prompt = f"""
Retrieved information:

{context}


User question:

{query}


Instructions:

Answer the user's question directly and concisely.

Use only the retrieved information above.

Do not include unrelated information.

Include the relevant source document and page number
when answering.
"""

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
