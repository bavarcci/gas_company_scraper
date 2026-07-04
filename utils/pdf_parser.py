"""
==========================================================
utils/pdf_parser.py

PDF Text Extraction Utility

Author: Ali Derakhshan
==========================================================
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


class PDFParser:
    """
    Extract text from PDF files.
    """

    def __init__(self):

        pass

    # -----------------------------------------------------

    def extract_text(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():

            raise FileNotFoundError(pdf_path)

        document = fitz.open(pdf_path)

        pages = []

        for page in document:

            text = page.get_text("text")

            if text:

                pages.append(text)

        document.close()

        return "\n".join(pages)

    # -----------------------------------------------------

    def extract_pages(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():

            raise FileNotFoundError(pdf_path)

        document = fitz.open(pdf_path)

        result = []

        for page_number, page in enumerate(document, start=1):

            result.append({

                "page": page_number,

                "text": page.get_text("text")

            })

        document.close()

        return result

    # -----------------------------------------------------

    def extract_metadata(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():

            raise FileNotFoundError(pdf_path)

        document = fitz.open(pdf_path)

        metadata = document.metadata

        document.close()

        return metadata