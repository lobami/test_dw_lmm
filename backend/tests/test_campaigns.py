import sys, os
# Use an in-memory SQLite DB for tests and enable TESTING so database.py uses StaticPool
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "1"
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def make_user(email, password, company_name=None):
    resp = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "company_name": company_name,
    })
    assert resp.status_code == 201
    return resp.json()


def login(email, password):
    resp = client.post("/auth/token", data={"username": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def sample_campaign_payload(name="camp1"):
    return {
        "name": name,
        "tipo_campania": "mensual",
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-01-31",
        "universo_zona_metro": 1000,
        "impactos_personas": 100,
        "impactos_vehiculos": 50,
        "frecuencia_calculada": 1.0,
        "frecuencia_promedio": 1.0,
        "alcance": 500,
        "nse_ab": 0.1,
        "nse_c": 0.1,
        "nse_cmas": 0.1,
        "nse_d": 0.1,
        "nse_dmas": 0.1,
        "nse_e": 0.1,
        "edad_0a14": 0.1,
        "edad_15a19": 0.1,
        "edad_20a24": 0.1,
        "edad_25a34": 0.1,
        "edad_35a44": 0.1,
        "edad_45a64": 0.1,
        "edad_65mas": 0.1,
        "hombres": 0.5,
        "mujeres": 0.5,
    }


def test_campaign_crud_and_isolation():
    # Create owner in Company A
    make_user("ownerA@example.com", "secretA", "CompanyA")
    tokenA = login("ownerA@example.com", "secretA")

    # Create campaign as ownerA (should be allowed)
    payload = sample_campaign_payload("campA1")
    resp = client.post("/campaigns/", json=payload, headers={"Authorization": f"Bearer {tokenA}"})
    assert resp.status_code == 201

    # List campaigns for ownerA
    resp = client.get("/campaigns/?skip=0&limit=10", headers={"Authorization": f"Bearer {tokenA}"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(c["name"] == "campA1" for c in data["data"]) if isinstance(data, dict) else False

    # Create user in Company B
    make_user("ownerB@example.com", "secretB", "CompanyB")
    tokenB = login("ownerB@example.com", "secretB")

    # ownerB should not see company A campaigns
    resp = client.get("/campaigns/?skip=0&limit=10", headers={"Authorization": f"Bearer {tokenB}"})
    assert resp.status_code == 200
    dataB = resp.json()
    assert dataB["total"] == 0 or all(c["company_id"] != data["data"][0].get("company_id") for c in dataB["data"]) 
