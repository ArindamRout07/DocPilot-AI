def flatten_document(pages):
    """
    Combine all pages into one continuous document while
    recording where each page starts.
    """

    document_text = ""
    page_boundaries = []

    current_position = 0

    for page in pages:
        page_boundaries.append(
            {
                "page_number": page["page"],
                "start": current_position
            }
        )

        document_text += page["text"] + "\n"

        current_position = len(document_text)

    return document_text, page_boundaries


def get_page_number(chunk_start, page_boundaries):
    """
    Determine which page a chunk belongs to based on its
    starting character position.
    """

    page_number = page_boundaries[0]["page_number"]

    for boundary in page_boundaries:
        if chunk_start >= boundary["start"]:
            page_number = boundary["page_number"]
        else:
            break

    return page_number


def chunk_document(document_text, chunk_size=200, overlap=40):
    """
    Split the entire document into overlapping word-based chunks.

    Parameters:
        chunk_size (int): Number of words in each chunk.
        overlap (int): Number of overlapping words between chunks.

    Returns:
        List of chunks containing text and approximate starting
        character position.
    """

    words = document_text.split()

    chunks = []
    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk_text = " ".join(words[start:end])

        # Approximate character position of the chunk
        char_position = len(" ".join(words[:start]))

        chunks.append(
            {
                "text": chunk_text,
                "start": char_position
            }
        )

        start += chunk_size - overlap

    return chunks


def create_chunks(document_name, pages, chunk_size=200, overlap=40):
    """
    Main chunking pipeline.

    Returns a list of chunk objects ready to be stored
    in the database.
    """

    document_text, page_boundaries = flatten_document(pages)

    raw_chunks = chunk_document(
        document_text=document_text,
        chunk_size=chunk_size,
        overlap=overlap
    )

    chunk_objects = []

    for index, chunk in enumerate(raw_chunks, start=1):

        page_number = get_page_number(
            chunk["start"],
            page_boundaries
        )

        chunk_objects.append(
            {
                "document_name": document_name,
                "page_number": page_number,
                "chunk_index": index,
                "chunk_text": chunk["text"]
            }
        )

    return chunk_objects