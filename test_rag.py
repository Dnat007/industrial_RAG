from src.rag import ask


query = "How many PTO days does an employee get after 6 years of service?"


response = ask(
    query=query,
    k=3,
    candidate_k=50,
    allowed_access_levels=["internal"],
)


print("\n" + "=" * 70)
print("RAG ANSWER")
print("=" * 70)

print(response["answer"])


print("\n" + "=" * 70)
print("SOURCES")
print("=" * 70)


for source in response["sources"]:

    print(
        f"{source['document_name']} "
        f"| Page: {source['page_number']}"
    )