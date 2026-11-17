# personal_AI_trainer
Personal AI Running Coach – Backend: [`backend/`](backend/README.md)

## Mit Docker starten

Die SQLite-Datenbank wird beim ersten Start automatisch angelegt und liegt im Volume `db-data`
(bleibt bei Neustarts und Rebuilds erhalten).

**Server (Linux, Ollama im Container, läuft auf der CPU):**

```bash
docker compose --profile ollama up -d --build
docker compose exec ollama ollama pull qwen2.5:0.5b   # einmalig, Modelle bleiben im Volume
```

**Mac (Ollama läuft nativ, weil Docker auf dem Mac keine GPU nutzen kann):**

```bash
cp .env.example .env   # darin OLLAMA_URL=http://host.docker.internal:11434 einkommentieren
docker compose up -d --build
```

API: http://localhost:8000/docs · Logs: `docker compose logs -f backend` · Stoppen: `docker compose --profile ollama down`

Modell wechseln: `OLLAMA_MODEL` in `.env` setzen, Modell pullen, `docker compose up -d`.
