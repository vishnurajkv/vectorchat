from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse, UploadResponse
from app.services.chat import ChatService
from app.services.document import DocumentService

app = FastAPI(title="Document Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService()
document_service = DocumentService()

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    content = await file.read()
    texts, metadatas = document_service.process_pdf(content)
    session_id = chat_service.create_session(texts, metadatas)
    
    return UploadResponse(session_id=session_id)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer, sources = chat_service.get_response(
        request.session_id,
        request.question,
        request.chat_history
    )
    return ChatResponse(answer=answer, sources=sources)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
