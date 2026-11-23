"""API tests use an isolated in-memory SQLite database."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test-placeholder.db")
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-long-enough-for-tests-123")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def register(client: TestClient, username: str = "snake_player") -> None:
    response = client.post("/api/register", json={"username": username, "password": "strong-pass-123"})
    assert response.status_code == 201


def login(client: TestClient, username: str = "snake_player") -> str:
    response = client.post("/api/login", json={"username": username, "password": "strong-pass-123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_checks_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_register_creates_account(client):
    response = client.post("/api/register", json={"username": "alice_1", "password": "strong-pass-123"})
    assert response.status_code == 201
    assert response.json()["username"] == "alice_1"


def test_register_rejects_duplicate_username(client):
    register(client)
    response = client.post("/api/register", json={"username": "snake_player", "password": "another-pass-123"})
    assert response.status_code == 409


def test_register_validates_password_length(client):
    response = client.post("/api/register", json={"username": "player", "password": "short"})
    assert response.status_code == 422


def test_login_returns_bearer_token(client):
    register(client)
    response = client.post("/api/login", json={"username": "snake_player", "password": "strong-pass-123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(client):
    register(client)
    response = client.post("/api/login", json={"username": "snake_player", "password": "wrong-pass-123"})
    assert response.status_code == 401


def test_score_requires_authentication(client):
    response = client.post("/api/scores", json={"score": 100})
    assert response.status_code == 401


def test_authenticated_user_can_submit_score(client):
    register(client)
    token = login(client)
    response = client.post("/api/scores", json={"score": 120}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["score"] == 120


def test_top_scores_are_ordered_and_limited_to_ten(client):
    register(client, "player_one")
    token = login(client, "player_one")
    for score in range(1, 13):
        client.post("/api/scores", json={"score": score}, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/api/scores/top")
    assert response.status_code == 200
    assert len(response.json()) == 10
    assert [row["score"] for row in response.json()] == list(range(12, 2, -1))


def test_score_rejects_negative_value(client):
    register(client)
    token = login(client)
    response = client.post("/api/scores", json={"score": -1}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422
