from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"ok": True}

def test_chat_endpoint():
    payload = {
        "message": "Biodiversity is declining on my land",
        "context": {
            "soil_organic_carbon_pct": 0.3,
            "rainfall_mm_annual": 350,
            "land_use": "monoculture wheat",
            "region": "semi-arid",
        },
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["session_id"]
    assert body["recommendations"]
