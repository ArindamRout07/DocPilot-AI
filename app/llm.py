import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def generate_answer(question, retrieved_chunks, include_sources=True):
    """
    Generate an answer using only the retrieved document context.

    Args:
        question (str): The user's question.
        retrieved_chunks (list): List of retrieved document chunks.
        include_sources (bool): If True, appends a plain-text "Sources:"
            section to the answer string (backward-compatible behavior).
            Set to False when the UI renders citations separately.

    Returns:
        str: The generated answer (with or without appended sources).
    """

    if not retrieved_chunks:
        return "I couldn't find that information in the document."

    context = "\n\n".join(
        item["chunk"] for item in retrieved_chunks
    )

    prompt = f"""
You are an AI assistant that answers questions strictly from the provided document context.

Instructions:
- Use ONLY the information in the context.
- Do NOT use your own knowledge.
- If the answer is not present in the context, reply exactly:
  "I couldn't find that information in the document."
- Do not guess or assume missing information.
- Keep the answer concise and professional.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise document question-answering assistant."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content.strip()

    if include_sources:

        # Build unique document/page citations
        sources = []

        for item in retrieved_chunks:
            source = (
                item["document_name"],
                item["page_number"]
            )

            if source not in sources:
                sources.append(source)

        answer += "\n\nSources:\n"

        for document_name, page_number in sources:
            answer += f"• {document_name} — Page {page_number}\n"

    return answer

