"""Provider-neutral LLM client.

The rest of the app only talks to `LLMClient`. `OllamaClient` is the real
implementation; `FakeLLMClient` is for tests and offline development.
A cloud provider can later be added as another implementation.
"""

import json
from collections.abc import AsyncIterator
from typing import Any, Literal, Protocol

import httpx
from pydantic import BaseModel

from app.config import settings


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMClient(Protocol):
    async def chat(
        self, messages: list[ChatMessage], json_schema: dict[str, Any] | None = None
    ) -> str:
        """Return the full answer. With `json_schema`, the answer is JSON matching it."""
        ...

    def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """Yield the answer piece by piece (for the chat UI)."""
        ...

    async def is_available(self) -> bool: ...


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _payload(self, messages: list[ChatMessage], stream: bool) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": stream,
        }

    async def chat(
        self, messages: list[ChatMessage], json_schema: dict[str, Any] | None = None
    ) -> str:
        payload = self._payload(messages, stream=False)
        if json_schema is not None:
            payload["format"] = json_schema  # Ollama structured output
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        payload = self._payload(messages, stream=True)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if text := chunk.get("message", {}).get("content"):
                        yield text
                    if chunk.get("done"):
                        break

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.is_success
        except httpx.HTTPError:
            return False


class FakeLLMClient:
    """Returns a canned answer. Used in tests."""

    def __init__(self, answer: str = "Hello from the fake coach."):
        self.answer = answer

    async def chat(
        self, messages: list[ChatMessage], json_schema: dict[str, Any] | None = None
    ) -> str:
        return self.answer

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        for word in self.answer.split(" "):
            yield word + " "

    async def is_available(self) -> bool:
        return True


def get_llm() -> LLMClient:
    """FastAPI dependency. Override it in tests with `FakeLLMClient`."""
    return OllamaClient(settings.ollama_url, settings.ollama_model)
