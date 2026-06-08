"""
Milestone 5: Grounded generation + Gradio interface.

Retrieves relevant chunks from ChromaDB, then uses Groq (llama-3.3-70b-versatile)
to generate an answer grounded only in the retrieved context.
Every response includes source attribution.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import gradio as gr
from retrieval import build_index, retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

_groq_client: Groq | None = None


def _get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set. Copy .env.example to .env and add your key.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


SYSTEM_PROMPT = """You are The Unofficial Guide — a helpful assistant that answers questions about off-campus housing near Boston-area universities (Northeastern, BU, MIT, Harvard, Tufts, Emerson).

CRITICAL RULES:
1. Answer ONLY using the information in the provided documents. Do not use your general knowledge.
2. If the documents do not contain enough information to answer the question, say exactly: "I don't have enough information in my sources to answer that question."
3. Always cite your sources inline using the format [source: filename]. Every factual claim must have a citation.
4. Do not make up facts, prices, addresses, or advice not present in the documents.
5. Be direct and specific — students need actionable information."""


def ask(question: str, k: int = 5) -> dict:
    """
    Full RAG pipeline: retrieve relevant chunks, generate grounded answer.
    Returns {answer, sources, chunks}.
    """
    chunks = retrieve(question, k=k)

    if not chunks:
        return {
            "answer": "I don't have enough information in my sources to answer that question.",
            "sources": [],
            "chunks": [],
        }

    # Build context block with source labels
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[Document: {chunk['source']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_parts)

    user_message = f"""Here are the relevant documents retrieved for this question:

{context}

---

Question: {question}

Answer using only the information in the documents above. Cite sources inline as [source: filename]."""

    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=800,
    )

    answer = response.choices[0].message.content.strip()

    # Programmatically collect unique sources from retrieved chunks
    sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {"answer": answer, "sources": sources, "chunks": chunks}


def handle_query(question: str):
    """Gradio handler: returns (answer_text, sources_text)."""
    if not question.strip():
        return "Please enter a question.", ""

    try:
        result = ask(question)
        answer = result["answer"]
        sources_text = "\n".join(f"• {s}" for s in result["sources"])
        return answer, sources_text
    except ValueError as e:
        return str(e), ""
    except Exception as e:
        return f"Error: {e}", ""


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="The Unofficial Guide — Boston Student Housing") as demo:
        gr.Markdown(
            """# 🏠 The Unofficial Guide: Boston Student Housing
            Ask anything about off-campus housing near Northeastern, BU, MIT, Harvard, Tufts, or Emerson.
            Answers are grounded in real student reviews and Reddit threads.
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                question_box = gr.Textbox(
                    label="Your question",
                    placeholder='e.g. "Is Mission Hill safe for college students?" or "What should I know about Allston landlords?"',
                    lines=2,
                )
                ask_btn = gr.Button("Ask", variant="primary")

        with gr.Row():
            with gr.Column(scale=3):
                answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)
            with gr.Column(scale=1):
                sources_box = gr.Textbox(label="Retrieved from", lines=10, interactive=False)

        gr.Examples(
            examples=[
                ["What do students say about landlords in Allston?"],
                ["Is Mission Hill safe for college students at night?"],
                ["Which neighborhoods near Northeastern have the cheapest rent?"],
                ["What lease red flags should Boston students watch out for?"],
                ["What are students' experiences with off-campus housing near Tufts?"],
            ],
            inputs=question_box,
        )

        ask_btn.click(handle_query, inputs=question_box, outputs=[answer_box, sources_box])
        question_box.submit(handle_query, inputs=question_box, outputs=[answer_box, sources_box])

    return demo


if __name__ == "__main__":
    print("Building/loading index...")
    build_index()
    print("Starting Gradio interface at http://localhost:7860\n")
    demo = build_ui()
    demo.launch()
