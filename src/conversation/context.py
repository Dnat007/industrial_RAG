def build_context(results) -> str:
    """
    Convert retrieved Azure AI Search results
    into a clean context for the LLM.
    """

    context_parts = []

    for i, result in enumerate(results, 1):

        content = result.get("content", "").strip()

        if not content:
            continue

        document_name = result.get(
            "document_name",
            "Unknown"
        )

        page_number = result.get(
            "page_number",
            "Unknown"
        )

        section = result.get(
            "section",
            ""
        )

        source = (
            f"{document_name}"
            f" | Page: {page_number}"
        )

        if section:
            source += f" | Section: {section}"

        context_parts.append(
            f"[Source {i}: {source}]\n"
            f"{content}"
        )

    return "\n\n".join(context_parts)