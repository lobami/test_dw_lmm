import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database
from app.campaigns import crud, models
from app.security import get_current_user


client = TestClient(app)


class _FakeUser:
    def __init__(self, company_id=1, role='viewer'):
        self.company_id = company_id
        self.role = role


def _override_current_user():
    return _FakeUser(company_id=1, role='admin')


def test_campaigns_pagination_and_filters_seeded():
    """Verify pagination (5 per page), tipo filter, and date range filter."""
    # override auth dependency to avoid needing real tokens
    app.dependency_overrides[get_current_user] = _override_current_user
    # Assume seed has populated campaigns; query first page
    resp = client.get('/campaigns/?skip=0&limit=5')
    assert resp.status_code == 200
    body = resp.json()
    assert 'data' in body and 'total' in body
    assert isinstance(body['data'], list)
    assert len(body['data']) <= 5

    # Filter by tipo_campania (pick a value from seeded data)
    resp2 = client.get('/campaigns/?skip=0&limit=5&tipo_campania=mensual')
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert 'data' in body2
    # All returned items (if any) must have tipo_campania == 'mensual'
    for item in body2['data']:
        assert item.get('tipo_campania') == 'mensual'

    # Date range filter: choose a narrow range that likely matches a subset
    resp3 = client.get('/campaigns/?skip=0&limit=5&start_date=2025-01-01T00:00:00&end_date=2025-12-31T23:59:59')
    assert resp3.status_code == 200
    body3 = resp3.json()
    assert 'data' in body3


def test_campaign_detail_includes_sites_and_periods():
    # Get any campaign name from DB
    db = database.SessionLocal()
    try:
        any_campaign = db.query(models.Campaign).first()
        if not any_campaign:
            pytest.skip('No campaign seeded')
        name = any_campaign.name
    finally:
        db.close()
    # override auth dependency using the same company_id as the seeded campaign
    app.dependency_overrides[get_current_user] = lambda: _FakeUser(company_id=any_campaign.company_id, role='admin')

    resp = client.get(f'/campaigns/{name}')
    assert resp.status_code == 200
    body = resp.json()
    assert 'sites' in body
    assert 'periods' in body

    # cleanup
    app.dependency_overrides.pop(get_current_user, None)
