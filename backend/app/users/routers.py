from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
import logging
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from . import crud as crud_users, schemas as schemas_users
from ..security import create_access_token, get_current_user
from ..security import role_required

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("app.users.routers")


@router.post("/token", response_model=schemas_users.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), response: Response = None):
    logger.info("login_attempt", extra={"email": form_data.username})
    user = crud_users.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        logger.warning("login_failed", extra={"email": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email}, token_type="access")
    # create opaque refresh token stored in DB and set as httpOnly cookie
    refresh_token = crud_users.create_refresh_token(db, user_id=user.id)
    # For cross-site XHR from the frontend we must set SameSite=None and Secure=True
    # and ensure the CORS middleware uses the exact frontend origin (not '*') with allow_credentials=True.
    response.set_cookie(
        key="refresh_token",
        value=refresh_token.token,
        httponly=True,
        samesite="none",
        secure=True,
        path='/',
    )
    logger.info("login_success", extra={"user_id": user.id, "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas_users.UserRead)
def read_users_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=schemas_users.UserRead, status_code=201)
def register_user(user_in: schemas_users.UserCreate = Body(...), db: Session = Depends(get_db)):
    existing = crud_users.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    company_id = None
    if user_in.company_name:
        company = crud_users.get_company_by_name(db, user_in.company_name)
        if not company:
            company = crud_users.create_company(db, user_in.company_name)
        company_id = company.id
    user = crud_users.create_user(db, email=user_in.email, password=user_in.password, company_id=company_id)
    logger.info("user_registered", extra={"user_id": user.id, "email": user.email, "company_id": company_id})
    return user


@router.post('/refresh', response_model=schemas_users.Token)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        logger.warning("refresh_missing_cookie")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    rt = crud_users.get_refresh_token(db, refresh_token)
    if not rt or rt.revoked or rt.expires_at < __import__('datetime').datetime.utcnow():
        logger.warning("refresh_invalid", extra={"token": refresh_token})
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")
    user_obj = rt.user
    access_token = create_access_token(data={"sub": user_obj.email}, token_type="access")
    new_rt = crud_users.rotate_refresh_token(db, old_token=refresh_token, user_id=user_obj.id)
    response.set_cookie(
        key="refresh_token",
        value=new_rt.token,
        httponly=True,
        samesite="none",
        secure=True,
        path='/',
    )
    logger.info("refresh_rotated", extra={"user_id": user_obj.id, "old_token": refresh_token, "new_token": new_rt.token})
    return {"access_token": access_token, "token_type": "bearer"}



# Owner-only: create users (admin/viewer) within the same company
@router.post('/create_user', response_model=schemas_users.UserRead, status_code=201)
def owner_create_user(user_in: schemas_users.OwnerCreateUser = Body(...), db: Session = Depends(get_db), current_user=Depends(role_required("owner"))):
    # Ensure owner belongs to a company
    company_id = getattr(current_user, 'company_id', None)
    if not company_id:
        raise HTTPException(status_code=400, detail="Owner has no associated company")
    # sanitize role
    role = user_in.role if user_in.role in ("admin", "viewer") else "viewer"
    user = crud_users.create_user(db, email=user_in.email, password=user_in.password, company_id=company_id, role=role)
    logger.info("owner_created_user", extra={"owner_id": current_user.id, "created_user_id": user.id, "role": role})
    return user


@router.post('/logout')
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    rt = request.cookies.get('refresh_token')
    if rt:
        crud_users.revoke_refresh_token(db, rt)
        logger.info("logout_revoked", extra={"token": rt})

    # To ensure browsers remove the cookie regardless of stored attributes,
    # overwrite it with an expired cookie that matches the SameSite/Secure attributes.
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        samesite="none",
        secure=True,
        path='/',
        max_age=0,
        expires=0,
    )
    logger.info("logout_success")
    return {"ok": True}
