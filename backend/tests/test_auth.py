import sys, os
# Use an in-memory SQLite DB for tests and enable TESTING so database.py uses StaticPool
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "1"
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_and_login():
    # Register user (creates company and owner)
    resp = client.post("/auth/register", json={
        "email": "owner@example.com",
        "password": "secret",
        "company_name": "TestCo"
    })
    assert resp.status_code == 201
    user = resp.json()
    assert user["email"] == "owner@example.com"
    assert user.get("company_id") is not None

    # Login
    resp = client.post("/auth/token", data={"username": "owner@example.com", "password": "secret"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # Me
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["email"] == "owner@example.com"
