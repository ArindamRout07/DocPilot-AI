from pathlib import Path

from app.ingestion import extract_pdf_text
from app.chunking import create_chunks
from app.storage import store_chunks
from app.embeddings import generate_embeddings


def process_pdf(pdf_path):
    print("Processing document...")
    print("=" * 50)

    # Step 1: Extract PDF
    pdf_data = extract_pdf_text(pdf_path)

    # Step 2: Create chunks
    chunk_objects = create_chunks(
        document_name=Path(pdf_path).name,
        pages=pdf_data["content"]
    )

    print(f"\n✅ Total chunks created: {len(chunk_objects)}")

    # Step 3: Generate embeddings
    chunk_objects = generate_embeddings(chunk_objects)

    print("✅ Embeddings generated.")

    # Step 4: Store everything
    store_chunks(chunk_objects)

    print("✅ Stored in PostgreSQL.")

    return chunk_objects