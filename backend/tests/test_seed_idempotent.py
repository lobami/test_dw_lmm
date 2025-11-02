import os
import sys
os.environ['TESTING'] = '1'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Ensure backend package root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
import seed
from seed import ensure_default_admin, load_data
from app.campaigns.models import Campaign
from app.users.models import Company, User


def test_seed_idempotent():
    db = SessionLocal()
    # run load_data (will create tables and load CSVs)
    load_data()
    ensure_default_admin()

    # count companies and admin user
    comp = db.query(Company).filter(Company.name == 'publicidad loth').all()
    assert len(comp) == 1

    admins = db.query(User).filter(User.email == 'admin@admin.com').all()
    assert len(admins) == 1

    # Run again - should not create duplicates
    load_data()
    ensure_default_admin()

    comp2 = db.query(Company).filter(Company.name == 'publicidad loth').all()
    assert len(comp2) == 1

    admins2 = db.query(User).filter(User.email == 'admin@admin.com').all()
    assert len(admins2) == 1

    db.close()
