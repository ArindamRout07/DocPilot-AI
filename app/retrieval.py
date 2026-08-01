import json

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.database import get_connection
from app.embeddings import model


def generate_query_embedding(query):
    """
    Generate an embedding for the user's question.
    """
    return model.encode(query).tolist()


def fetch_chunks_from_db():
    """
    Fetch all chunks along with document metadata and embeddings
    from PostgreSQL.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.document_name,
            c.page_number,
            c.chunk_text,
            c.embedding
        FROM document_chunks c
        JOIN documents d
            ON c.document_id = d.id
        ORDER BY c.id;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    chunk_data = []

    for document_name, page_number, chunk_text, embedding in rows:

        if isinstance(embedding, str):
            embedding = json.loads(embedding)

        chunk_data.append(
            {
                "document_name": document_name,
                "page_number": page_number,
                "chunk": chunk_text,
                "embedding": embedding
            }
        )

    return chunk_data


def retrieve_chunks(
    query,
    top_k=3,
    similarity_threshold=0.20
):
    """
    Retrieve the most relevant chunks for a user query.
    """

    query_embedding = np.array(
        generate_query_embedding(query)
    ).reshape(1, -1)

    chunk_data = fetch_chunks_from_db()

    chunk_embeddings = np.array(
        [item["embedding"] for item in chunk_data]
    )

    scores = cosine_similarity(
        query_embedding,
        chunk_embeddings
    )[0]

    top_indices = np.argsort(scores)[::-1]

    results = []

    for index in top_indices:

        score = float(scores[index])

        if score < similarity_threshold:
            continue

        results.append(
            {
                "document_name": chunk_data[index]["document_name"],
                "page_number": chunk_data[index]["page_number"],
                "chunk": chunk_data[index]["chunk"],
                "score": score
            }
        )

        if len(results) == top_k:
            break

    return results