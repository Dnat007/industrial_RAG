from src.generation.prompt import build_prompt
from src.generation.llm import generate_answer


query = "What is the leave policy?"

context = """
[Source 1: LeavePolicy.pdf | Page: 1]
Employees are entitled to 18 days of annual leave per year.

[Source 2: LeavePolicy.pdf | Page: 2]
Unused leave can be carried forward according to company policy.
"""


messages = build_prompt(
    query=query,
    context=context,
)


answer = generate_answer(messages)


print("\n" + "=" * 70)
print("LLM ANSWER")
print("=" * 70)
print(answer)
