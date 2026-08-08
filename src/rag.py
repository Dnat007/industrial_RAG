import time

from src.retrieval.reranker import rerank
from src.conversation.context import build_context
from src.generation.prompt import build_prompt
from src.generation.llm import generate_answer


def ask(
    query: str,
    k: int = 5,
    candidate_k: int = 50,
    allowed_access_levels: list[str] | None = None,
    departments: list[str] | None = None,
    versions: list[str] | None = None,
    document_ids: list[str] | None = None,
) -> dict:

    # total_start = time.perf_counter()
    # retrieval_start = time.perf_counter()
    results = rerank(
        query=query,
        k=k,
        candidate_k=candidate_k,
        allowed_access_levels=allowed_access_levels,
        departments=departments,
        versions=versions,
        document_ids=document_ids,
    )

    # retrieval_time = (time.perf_counter() - retrieval_start)
    # context_start = time.perf_counter()
    context = build_context(results)
    # context_time = (time.perf_counter() - context_start)
    # prompt_start = time.perf_counter()

    messages = build_prompt(query=query,context=context)
    # prompt_time = (time.perf_counter() - prompt_start)

    # llm_start = time.perf_counter()
    answer = generate_answer(messages)
    # llm_time = (time.perf_counter() - llm_start)


    # total_time = (time.perf_counter() - total_start)

    # print("\n")
    # print("=" * 50)
    # print("LATENCY")
    # print("=" * 50)
    # print(f"Retrieval : {retrieval_time:.2f} sec")
    # print(f"Context   : {context_time:.2f} sec")
    # print(f"Prompt    : {prompt_time:.2f} sec")
    # print(f"LLM      : {llm_time:.2f} sec")
    # print(f"Total     : {total_time:.2f} sec")
    # print("=" * 50)
    sources = []

    for result in results:

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
    }