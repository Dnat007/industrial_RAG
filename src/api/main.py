from src.rag import ask

def main():
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
                k=5,
                candidate_k=50,
                allowed_access_levels=[
                    "internal"
                ],
            )
# remove the source part from the end its use less as of now
            answer = response["answer"]

            lines = answer.strip().splitlines()

            if lines and lines[-1].strip().startswith("(Source:"):
                lines.pop()

            answer = "\n".join(lines).strip()

            print("\nAssistant:")
            print(answer)
            print()

        except Exception as e:

            print("\nError:")
            print(str(e))

if __name__ == "__main__":
    main()
