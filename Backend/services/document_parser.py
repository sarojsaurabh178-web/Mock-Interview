import io
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple
from pypdf import PdfReader


class DocumentParser:
    """
    Parser service to extract clean text and metadata from PDF, DOCX, DOC, and TXT files.
    """

    SUPPORTED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "md"}

    @classmethod
    def parse_file(cls, filename: str, content: bytes) -> Tuple[str, int]:
        """
        Parses document bytes and returns (extracted_text, page_count).
        """
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported document format '.{ext}'. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}")

        if not content or len(content) == 0:
            raise ValueError("Document file is empty.")

        if ext == "pdf":
            return cls.parse_pdf(content)
        elif ext in {"docx", "doc"}:
            return cls.parse_docx(content)
        elif ext in {"txt", "md"}:
            return cls.parse_text(content)
        else:
            return cls.parse_text(content)

    @staticmethod
    def parse_pdf(content: bytes) -> Tuple[str, int]:
        """Extract text and page count from PDF bytes using pypdf."""
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = reader.pages
            page_count = max(len(pages), 1)
            text_blocks = []
            for page in pages:
                extracted = page.extract_text()
                if extracted:
                    text_blocks.append(extracted)
            full_text = "\n\n".join(text_blocks).strip()
            return full_text, page_count
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @staticmethod
    def parse_docx(content: bytes) -> Tuple[str, int]:
        """Extract text from Word (.docx) files using standard zipfile XML reading."""
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as docx_zip:
                xml_content = docx_zip.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                
                paragraphs = []
                for p in tree.iterfind(".//w:p", namespaces):
                    texts = [node.text for node in p.iterfind(".//w:t", namespaces) if node.text]
                    if texts:
                        paragraphs.append("".join(texts))
                
                text = "\n".join(paragraphs).strip()
                page_count = max(1, len(text.split("\n\n")))
                return text, page_count
        except Exception:
            # Fallback text decoding if not a standard zipped docx
            decoded = content.decode("utf-8", errors="ignore").strip()
            return decoded, 1

    @staticmethod
    def parse_text(content: bytes) -> Tuple[str, int]:
        """Decode plain text or markdown files."""
        text = content.decode("utf-8", errors="ignore").strip()
        page_count = max(1, len(text.splitlines()) // 50)
        return text, page_count
