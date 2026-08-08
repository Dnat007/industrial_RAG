from src.rag import ask


def main():

    print("=" * 70)
    print("ENTERPRISE RAG ASSISTANT")
    print("=" * 70)

    print("\nType 'exit' or 'quit' to stop.\n")

    while True:

        query = input("You: ").strip()

        if not query:
            continue

        if query.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break

        try:

            response = ask(
                query=query,

                # Final number of results
                k=5,

                # Candidate pool for semantic reranking
                candidate_k=50,

                # Current demo security scope
                allowed_access_levels=[
                    "internal"
                ],
            )

            # --------------------------------------------------
            # Remove source citation from the final answer
            # --------------------------------------------------

            answer = response["answer"]

            lines = answer.strip().splitlines()

            if lines and lines[-1].strip().startswith("(Source:"):
                lines.pop()

            answer = "\n".join(lines).strip()

            # --------------------------------------------------
            # Print only the clean answer
            # --------------------------------------------------

            print("\nAssistant:")
            print(answer)

            print()

        except Exception as e:

            print("\nError:")
            print(str(e))

        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    main()
