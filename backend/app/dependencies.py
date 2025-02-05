from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from .config import get_settings

settings = get_settings()

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

def get_llm():
    return HuggingFaceEndpoint(
        repo_id=settings.model_repo_id,
        task="text-generation",
        temperature=settings.temperature,
        max_length=settings.max_length,
        token=settings.huggingface_api_token
    )
