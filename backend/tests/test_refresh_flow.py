from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_refresh_cookie_flow():
    email = "refresh_test@example.com"
    password = "secret"

    # Register user (idempotent if already exists)
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 201)

    # helper to safely get most-recent cookie value (httpx may have multiple cookies stored)
    def _get_cookie_value(name: str):
        for c in reversed(list(client.cookies.jar)):
            if c.name == name:
                return c.value
        return None

    # Login: should set httpOnly refresh cookie and return access token
    r = client.post("/auth/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data
    # Test client should have received and stored the cookie
    cookie = _get_cookie_value('refresh_token')
    assert cookie is not None

    old_cookie = cookie

    # Ensure cookie is present in cookie jar for the refresh request
    client.cookies.set('refresh_token', old_cookie)

    # Use refresh endpoint - client will send cookie automatically
    r2 = client.post("/auth/refresh")
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert "access_token" in data2
    # get new cookie safely
    new_cookie = _get_cookie_value('refresh_token')
    assert new_cookie is not None
    # rotation should create a different token
    assert new_cookie != old_cookie

    # Logout should revoke refresh token and clear cookie
    # ensure client sends the new refresh cookie when calling logout
    client.cookies.set('refresh_token', new_cookie)
    r3 = client.post("/auth/logout")
    assert r3.status_code == 200
    # server should have revoked the token in DB
    from app.database import SessionLocal as _SessionLocal
    db = _SessionLocal()
    from app.users import crud as crud_users
    token_in_db = crud_users.get_refresh_token(db, new_cookie)
    assert token_in_db is not None and token_in_db.revoked
    db.close()

    # Further refresh attempts should fail
    r4 = client.post("/auth/refresh")
    assert r4.status_code == 401
