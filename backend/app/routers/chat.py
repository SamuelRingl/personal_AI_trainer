"""Chat with the coach, streamed to the client via Server-Sent Events (SSE).

The client sends the full conversation so far; nothing is stored yet.
SSE events: `data: {"type": "token", "text": "..."}`, then `{"type": "done"}`
or `{"type": "error", "detail": "..."}`.
"""

import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.deps import CurrentUser
from app.llm import ChatMessage, LLMClient, get_llm
from app.models import UserProfile

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


def system_prompt(user: UserProfile) -> ChatMessage:
    # TODO: replace with a proper prompt once the coach behaviour is defined.
    profile = {
        "name": user.name,
        "goal": user.goal,
        "weekly_km": user.weekly_km,
        "days_per_week": user.days_per_week,
        "blocked_weekdays": user.blocked_weekdays,
    }
    return ChatMessage(
        role="system",
        content=(
            "You are a friendly, careful running coach. Keep answers short. "
            f"Runner profile: {json.dumps(profile)}"
        ),
    )


def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.post("/chat")
async def chat(
    req: ChatRequest,
    user: CurrentUser,
    llm: Annotated[LLMClient, Depends(get_llm)],
) -> StreamingResponse:
    messages = [system_prompt(user), *req.messages]

    async def events() -> AsyncIterator[str]:
        try:
            async for text in llm.stream_chat(messages):
                yield sse({"type": "token", "text": text})
            yield sse({"type": "done"})
        except Exception as e:  # stream is already open, so report errors as an event
            yield sse({"type": "error", "detail": str(e)})

    return StreamingResponse(events(), media_type="text/event-stream")
