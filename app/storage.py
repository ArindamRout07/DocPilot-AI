import json

from app.database import get_connection


def store_chunks(chunk_objects):
    """
    Store chunk objects and their embeddings in PostgreSQL.
    Prevents duplicate document ingestion.
    """

    if not chunk_objects:
        return

    conn = get_connection()
    cur = conn.cursor()

    document_name = chunk_objects[0]["document_name"]

    # Check if document already exists
    cur.execute(
        """
        SELECT id
        FROM documents
        WHERE document_name = %s
        """,
        (document_name,)
    )

    result = cur.fetchone()

    if result:
        print(f"Document '{document_name}' already exists. Skipping ingestion.")

        cur.close()
        conn.close()
        return

    # Insert new document
    cur.execute(
        """
        INSERT INTO documents (document_name)
        VALUES (%s)
        RETURNING id
        """,
        (document_name,)
    )

    document_id = cur.fetchone()[0]

    print(f"Inserted document '{document_name}'.")

    # Insert chunks + embeddings
    insert_query = """
    INSERT INTO document_chunks
    (
        document_id,
        page_number,
        chunk_index,
        chunk_text,
        embedding
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for chunk in chunk_objects:

        cur.execute(
            insert_query,
            (
                document_id,
                chunk["page_number"],
                chunk["chunk_index"],
                chunk["chunk_text"],
                json.dumps(chunk["embedding"])
            )
        )

    conn.commit()

    print(f"Stored {len(chunk_objects)} chunks successfully.")

    cur.close()
    conn.close()