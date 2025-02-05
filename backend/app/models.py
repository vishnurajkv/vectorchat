from pydantic import BaseModel
from typing import List, Tuple

class ChatRequest(BaseModel):
    question: str
    chat_history: List[Tuple[str, str]]
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class UploadResponse(BaseModel):
    session_id: str
