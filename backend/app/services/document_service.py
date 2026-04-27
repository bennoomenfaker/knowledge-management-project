from typing import Optional
import re
from io import BytesIO
import httpx


class DocumentService:
    def __init__(self):
        pass
    
    async def extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        try:
            import fitz
            
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            return text.strip() if text else None
        except ImportError:
            return await self._extract_text_fallback(pdf_content)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    
    async def _extract_text_fallback(self, pdf_content: bytes) -> Optional[str]:
        try:
            import pdfplumber
            
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            return text.strip() if text else None
        except Exception as e:
            print(f"PDF extraction fallback error: {e}")
            return None
    
    async def get_pdf_metadata(self, pdf_content: bytes) -> dict:
        try:
            import fitz
            
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            metadata = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
            }
            doc.close()
            return metadata
        except Exception as e:
            print(f"PDF metadata error: {e}")
            return {"page_count": 0}
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-àâäéèêëïîôùûüçœæ]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    async def get_file_size(self, pdf_content: bytes) -> int:
        return len(pdf_content)


def get_document_service() -> DocumentService:
    return DocumentService()