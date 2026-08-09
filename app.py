from flask import Flask, render_template, request, jsonify
from src.rag import ask

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask_route():
    data = request.get_json()
    query = data.get("message", "").strip()

    if not query:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = ask(
            query=query,
            k=5,
            candidate_k=50,
            allowed_access_levels=["internal"],
        )

        answer = response["answer"]
        lines = answer.strip().splitlines()

        if lines and lines[-1].strip().startswith("(Source:"):
            lines.pop()

        answer = "\n".join(lines).strip()

        return jsonify({"response": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
