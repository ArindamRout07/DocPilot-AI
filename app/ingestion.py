import importlib
from pathlib import Path

fitz = importlib.import_module("pymupdf")


def extract_pdf_text(pdf_path):
    """
    Extract text from every page of a PDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        dict: Extracted text and metadata.
    """

    try:
        pdf = fitz.open(pdf_path)

        total_pages = len(pdf)
        total_characters = 0

        extracted_pages = []

        print("=" * 50)
        print("Starting PDF Extraction...")
        print("=" * 50)

        for page_number, page in enumerate(pdf, start=1):

            text = page.get_text()

            total_characters += len(text)

            extracted_pages.append(
                {
                    "page": page_number,
                    "text": text
                }
            )

            print(f"✓ Page {page_number} extracted ({len(text)} characters)")

        pdf.close()

        print("\n" + "=" * 50)
        print("Document Summary")
        print("=" * 50)
        print(f"Pages       : {total_pages}")
        print(f"Characters  : {total_characters}")
        print("Status      : Extraction Successful")
        print("=" * 50)

        return {
            "pages": total_pages,
            "characters": total_characters,
            "content": extracted_pages
        }

    except FileNotFoundError:
        print("❌ PDF file not found.")

    except Exception as e:
        print(f"❌ Error: {e}")


