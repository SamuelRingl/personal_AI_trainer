# Backend – Personal AI Trainer

FastAPI + SQLite (SQLModel) + Ollama.

## Setup (einmalig)

```bash
brew install uv              # Paketmanager (ersetzt venv + pip)
cd backend
uv sync                      # legt .venv an und installiert alles aus uv.lock
cp .env.example .env         # Einstellungen (Modell, DB, CORS)
ollama pull qwen2.5:0.5b     # oder das Modell aus .env
```

## Starten

```bash
uv run uvicorn app.main:app --reload
```

API-Doku: http://localhost:8000/docs

## Tests

```bash
uv run pytest
```

## Pakete hinzufügen

```bash
uv add <paket>          # Laufzeit
uv add --dev <paket>    # nur Entwicklung
```

## Struktur

| Datei | Inhalt |
|---|---|
| `app/main.py` | App, CORS, Router |
| `app/config.py` | Einstellungen aus `.env` |
| `app/db.py` | SQLite-Engine, Session, `create_all()` beim Start |
| `app/models.py` | Tabellen (`user_profile`) und API-Schemas |
| `app/deps.py` | `get_current_user` (vorerst Header `X-User-Id`, später Token) |
| `app/llm.py` | `LLMClient`-Interface, `OllamaClient`, `FakeLLMClient` |
| `app/routers/` | `health`, `users`, `chat` |

## Endpunkte

| Methode | Pfad | |
|---|---|---|
| GET | `/api/health` | Status + ob Ollama erreichbar ist |
| POST | `/api/users` | User/Profil anlegen |
| GET / PUT | `/api/me/profile` | Eigenes Profil lesen / ändern (Header `X-User-Id`) |
| POST | `/api/chat` | Chat, Antwort als SSE-Stream (`token` … `done` / `error`) |
