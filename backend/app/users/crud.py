from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import logging

from . import models
from ..security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str):
    logger = logging.getLogger("app.users.crud")
    logger.debug("get_user_by_email", extra={"email": email})
    return db.query(models.User).filter(models.User.email == email).first()


def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()


def create_company(db: Session, name: str):
    logger = logging.getLogger("app.users.crud")
    # avoid using reserved LogRecord keys like 'name' or 'module' in extra
    logger.info("create_company", extra={"company_name": name})
    company = models.Company(name=name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def create_user(db: Session, email: str, password: str, company_id: int = None, role: str = "viewer"):
    logger = logging.getLogger("app.users.crud")
    logger.info("create_user_start", extra={"email": email, "company_id": company_id})
    hashed = get_password_hash(password)
    # If company_id is provided and there are no users in that company, make this user the owner
    if company_id is not None:
        existing = db.query(models.User).filter(models.User.company_id == company_id).count()
        if existing == 0:
            role = "owner"

    user = models.User(email=email, hashed_password=hashed, company_id=company_id, is_active=True, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("create_user_done", extra={"user_id": user.id, "email": email})
    return user


def authenticate_user(db: Session, email: str, password: str):
    logger = logging.getLogger("app.users.crud")
    user = get_user_by_email(db, email)
    if not user:
        logger.debug("authenticate_user_no_user", extra={"email": email})
        return False
    if not verify_password(password, user.hashed_password):
        logger.debug("authenticate_user_bad_password", extra={"email": email})
        return False
    return user


def create_refresh_token(db: Session, user_id: int, expires_in_days: int = 7):
    logger = logging.getLogger("app.users.crud")
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    rt = models.RefreshToken(token=token, user_id=user_id, expires_at=expires_at, revoked=False)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    logger.info("create_refresh_token", extra={"user_id": user_id, "token": token})
    return rt


def get_refresh_token(db: Session, token: str):
    logger = logging.getLogger("app.users.crud")
    logger.debug("get_refresh_token", extra={"token": token})
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()


def revoke_refresh_token(db: Session, token: str):
    logger = logging.getLogger("app.users.crud")
    logger.info("revoke_refresh_token_request", extra={"token": token})
    rt = get_refresh_token(db, token)
    if not rt:
        logger.warning("revoke_refresh_token_not_found", extra={"token": token})
        return False
    rt.revoked = True
    db.add(rt)
    db.commit()
    logger.info("revoke_refresh_token_done", extra={"token": token})
    return True


def rotate_refresh_token(db: Session, old_token: str, user_id: int, expires_in_days: int = 7):
    logger = logging.getLogger("app.users.crud")
    logger.info("rotate_refresh_token", extra={"old_token": old_token, "user_id": user_id})
    old = get_refresh_token(db, old_token)
    if old:
        old.revoked = True
        db.add(old)
        db.commit()
        logger.debug("rotate_refresh_token_old_revoked", extra={"old_token": old_token})
    new = create_refresh_token(db, user_id=user_id, expires_in_days=expires_in_days)
    logger.info("rotate_refresh_token_done", extra={"new_token": new.token, "user_id": user_id})
    return new
