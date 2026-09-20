"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.store import get_store


@pytest.fixture()
def client() -> TestClient:
    get_store().clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    get_store().clear()


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_mention_flow(client: TestClient) -> None:
    resp = client.post("/api/v1/mentions", json={"source": "x", "text": "Love it, great!"})
    assert resp.status_code == 200
    assert resp.json()["label"] == "positive"
    listed = client.get("/api/v1/mentions")
    assert len(listed.json()) == 1


def test_sentiment_and_digest(client: TestClient) -> None:
    client.post("/api/v1/mentions", json={"source": "x", "text": "Love it, great!"})
    client.post("/api/v1/mentions", json={"source": "x", "text": "Terrible awful crash"})
    summary = client.get("/api/v1/sentiment").json()
    assert summary["total"] == 2
    assert summary["index"] == 0.0
    digest = client.get("/api/v1/digest").json()["digest_md"]
    assert "Brand digest" in digest


def test_rejects_empty_text(client: TestClient) -> None:
    resp = client.post("/api/v1/mentions", json={"source": "x", "text": "   "})
    assert resp.status_code == 422


@pytest.mark.integration()
def test_alerts_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: алерты, без сети."""
    for _ in range(3):
        client.post("/api/v1/mentions", json={"source": "x", "text": "Terrible awful crash"})
    resp = client.get("/api/v1/alerts")
    assert resp.status_code == 200
    assert resp.json()[0]["kind"] == "negative_spike"
