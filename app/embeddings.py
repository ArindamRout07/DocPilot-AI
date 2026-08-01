from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunk_objects):
    """
    Generate embeddings for each chunk and attach them
    directly to the chunk object.
    """

    texts = [chunk["chunk_text"] for chunk in chunk_objects]

    embeddings = model.encode(texts)

    for chunk, embedding in zip(chunk_objects, embeddings):
        chunk["embedding"] = embedding.tolist()

    return chunk_objects