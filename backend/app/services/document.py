from typing import List, Dict, Tuple
import PyPDF2
from fastapi import HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config import get_settings

settings = get_settings()

class DocumentService:
    @staticmethod
    def process_pdf(file_content: bytes) -> Tuple[List[str], List[Dict]]:
        try:
            reader = PyPDF2.PdfReader(file_content)
            document = ""
            for page in reader.pages:
                document += page.extract_text()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            texts = text_splitter.split_text(document)
            metadatas = [{"source": f"page-{i+1}"} for i in range(len(texts))]
            return texts, metadatas
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing PDF: {str(e)}"
            )
