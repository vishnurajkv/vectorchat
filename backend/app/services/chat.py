from typing import Dict, List, Tuple
import uuid
from fastapi import HTTPException
from langchain_chroma import Chroma
from langchain.chains import ConversationalRetrievalChain
from ..dependencies import get_embeddings, get_llm
from ..config import get_settings

settings = get_settings()

class ChatService:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.llm = get_llm()
        self.sessions: Dict[str, ConversationalRetrievalChain] = {}

    def create_session(self, texts: List[str], metadatas: List[Dict]) -> str:
        try:
            session_id = str(uuid.uuid4())
            vectordb = Chroma.from_texts(
                texts,
                self.embeddings,
                metadatas=metadatas,
                persist_directory=f"{settings.persist_directory}/{session_id}"
            )
            retriever = vectordb.as_retriever(search_kwargs={"k": 3})
            self.sessions[session_id] = ConversationalRetrievalChain.from_llm(
                self.llm,
                retriever,
                return_source_documents=True
            )
            return session_id
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating chat session: {str(e)}"
            )

    def get_response(
        self,
        session_id: str,
        question: str,
        chat_history: List[Tuple[str, str]]
    ) -> Tuple[str, List[str]]:
        if session_id not in self.sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        try:
            qa_chain = self.sessions[session_id]
            result = qa_chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            
            sources = [doc.metadata["source"] for doc in result["source_documents"]]
            return result["answer"], sources
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting response: {str(e)}"
            )
