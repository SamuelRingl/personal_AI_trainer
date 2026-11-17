from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import settings
from app.llm import LLMClient, get_llm

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(llm: Annotated[LLMClient, Depends(get_llm)]) -> dict:
    return {
        "status": "ok",
        "llm_available": await llm.is_available(),
        "model": settings.ollama_model,
    }
