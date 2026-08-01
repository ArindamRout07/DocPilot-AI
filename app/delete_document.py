from pathlib import Path

from app.database import get_connection


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "data" / "pdfs"


def delete_document(document_name: str):
    """
    Deletes a document from both:
    1. PostgreSQL
    2. data/pdfs folder
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        # Find document id
        cur.execute(
            """
            SELECT id
            FROM documents
            WHERE document_name = %s
            """,
            (document_name,)
        )

        result = cur.fetchone()

        if result is None:

            print("Document not found.")
            return False

        document_id = result[0]

        # Delete chunks first
        cur.execute(
            """
            DELETE FROM document_chunks
            WHERE document_id = %s
            """,
            (document_id,)
        )

        # Delete document
        cur.execute(
            """
            DELETE FROM documents
            WHERE id = %s
            """,
            (document_id,)
        )

        conn.commit()

    finally:

        cur.close()
        conn.close()

    # Delete PDF file
    pdf_path = UPLOAD_FOLDER / document_name

    if pdf_path.exists():
        pdf_path.unlink()

    return True