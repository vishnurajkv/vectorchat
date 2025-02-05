from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import chromadb
import os
import uuid
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
import PyPDF2
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
PERSIST_DIRECTORY = "db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class ChatRequest(BaseModel):
    question: str
    chat_history: List[tuple[str, str]]
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

def process_pdf(file_content: bytes) -> tuple[List[str], List[Dict]]:
    try:
        reader = PyPDF2.PdfReader(file_content)
        document = ""
        for page in reader.pages:
            document += page.extract_text()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        texts = text_splitter.split_text(document)
        metadatas = [{"source": f"page-{i+1}"} for i in range(len(texts))]
        return texts, metadatas
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

class DocumentChat:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
        self.llm = HuggingFaceEndpoint(
            repo_id="google/flan-t5-xl",
            task="text-generation",
            temperature=0.5,
            max_length=512
        )
        self.sessions: Dict[str, ConversationalRetrievalChain] = {}

    def create_session(self, texts: List[str], metadatas: List[Dict]) -> str:
        session_id = str(uuid.uuid4())
        vectordb = Chroma.from_texts(
            texts,
            self.embeddings,
            metadatas=metadatas,
            persist_directory=f"{PERSIST_DIRECTORY}/{session_id}"
        )
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        self.sessions[session_id] = ConversationalRetrievalChain.from_llm(
            self.llm,
            retriever,
            return_source_documents=True
        )
        return session_id

    def get_response(self, session_id: str, question: str, chat_history: List[tuple[str, str]]) -> tuple[str, List[str]]:
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        qa_chain = self.sessions[session_id]
        result = qa_chain.invoke({
            "question": question,
            "chat_history": chat_history
        })
        
        sources = [doc.metadata["source"] for doc in result["source_documents"]]
        return result["answer"], sources

# Initialize document chat
doc_chat = DocumentChat()

@app.post("/upload")
async def upload_file(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    texts, metadatas = process_pdf(content)
    session_id = doc_chat.create_session(texts, metadatas)
    
    return {"session_id": session_id}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer, sources = doc_chat.get_response(
        request.session_id,
        request.question,
        request.chat_history
    )
    return ChatResponse(answer=answer, sources=sources)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
