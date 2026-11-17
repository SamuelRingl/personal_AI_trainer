import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.llm import FakeLLMClient, get_llm
from app.main import app


@pytest.fixture
def client():
    # Fresh in-memory database per test.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_llm] = lambda: FakeLLMClient("Easy run today.")
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user_id(client) -> int:
    r = client.post("/api/users", json={"name": "Anna", "weekly_km": 20})
    return r.json()["id"]
