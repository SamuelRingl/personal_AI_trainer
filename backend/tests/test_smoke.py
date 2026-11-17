import json


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_update_profile(client, user_id):
    headers = {"X-User-Id": str(user_id)}

    r = client.get("/api/me/profile", headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Anna"

    r = client.put(
        "/api/me/profile",
        headers=headers,
        json={"days_per_week": 4, "blocked_weekdays": ["tue"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["days_per_week"] == 4
    assert body["blocked_weekdays"] == ["tue"]
    assert body["weekly_km"] == 20  # untouched


def test_profile_requires_user(client):
    assert client.get("/api/me/profile").status_code == 401
    assert client.get("/api/me/profile", headers={"X-User-Id": "999"}).status_code == 404


def test_chat_streams_sse(client, user_id):
    r = client.post(
        "/api/chat",
        headers={"X-User-Id": str(user_id)},
        json={"messages": [{"role": "user", "content": "What should I run today?"}]},
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    events = [json.loads(line[6:]) for line in r.text.splitlines() if line.startswith("data: ")]
    text = "".join(e["text"] for e in events if e["type"] == "token")
    assert text.strip() == "Easy run today."
    assert events[-1]["type"] == "done"
