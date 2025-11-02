import os
import sys
os.environ['TESTING'] = '1'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Ensure backend package root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.users import crud as crud_users

client = TestClient(app)


def test_refresh_rotate_and_logout():
    db = SessionLocal()
    # register user via endpoint
    resp = client.post('/auth/register', json={'email': 't1@example.com', 'password': 'pass'})
    assert resp.status_code in (200, 201)

    # helper to safely get the most-recent cookie value by name (httpx may store multiple)
    def _get_cookie_value(name: str):
        # iterate reversed to prefer the most recently set cookie
        for c in reversed(list(client.cookies.jar)):
            if c.name == name:
                return c.value
        return None

    # login
    resp = client.post('/auth/token', data={'username': 't1@example.com', 'password': 'pass'})
    assert resp.status_code == 200
    assert 'access_token' in resp.json()
    # cookie set
    rt = _get_cookie_value('refresh_token')
    assert rt is not None

    # get the RefreshToken from DB
    rt_obj = crud_users.get_refresh_token(db, rt)
    assert rt_obj is not None
    old_token = rt_obj.token

    # call refresh -> should rotate. Ensure the client cookie jar contains the token.
    client.cookies.set('refresh_token', old_token)
    resp2 = client.post('/auth/refresh')
    assert resp2.status_code == 200
    new_rt_cookie = _get_cookie_value('refresh_token')
    assert new_rt_cookie is not None
    assert new_rt_cookie != old_token

    # old token should be revoked
    # Re-query in a fresh session to observe committed changes
    from app.database import SessionLocal as _SessionLocal
    db2 = _SessionLocal()
    old_rt_db = crud_users.get_refresh_token(db2, old_token)
    assert old_rt_db is not None and old_rt_db.revoked
    db2.close()

    # logout (ensure client cookie jar used)
    client.cookies.set('refresh_token', new_rt_cookie)
    resp3 = client.post('/auth/logout')
    assert resp3.status_code == 200
    # server should have revoked the token in DB
    db3 = _SessionLocal()
    token_after_logout = crud_users.get_refresh_token(db3, new_rt_cookie)
    assert token_after_logout is not None and token_after_logout.revoked
    db3.close()
    # response should include a Set-Cookie clearing the refresh token
    set_cookie_hdr = resp3.headers.get('set-cookie', '')
    assert 'refresh_token=' in set_cookie_hdr

    db.close()
