import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db

# Read from env or use defaults (in production, set a secure SECRET_KEY)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Use pbkdf2_sha256 first for compatibility in test environments where bcrypt
# native backend may cause issues. Keep bcrypt as an accepted scheme for
# existing hashes.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = "access"):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    # include token type for clarity
    to_encode.update({"typ": token_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[str]:
    """Verify refresh token and return subject (email) if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("typ") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def generate_refresh_token_db(db: Session, user_id: int, expires_in_days: int = REFRESH_TOKEN_EXPIRE_DAYS):
    """Create an opaque refresh token entry in DB and return the token string."""
    from .users import crud as users_crud

    rt = users_crud.create_refresh_token(db, user_id=user_id, expires_in_days=expires_in_days)
    return rt.token


def verify_refresh_token_db(db: Session, token: str):
    """Verify an opaque refresh token stored in DB. Returns user object if valid, otherwise None."""
    from .users import crud as users_crud

    rt = users_crud.get_refresh_token(db, token)
    if not rt:
        return None
    if rt.revoked:
        return None
    if rt.expires_at is not None:
        if rt.expires_at < datetime.utcnow():
            return None
    # return the user for convenience
    return rt.user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from .users.schemas import TokenData

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    from .users import crud as users_crud

    user = users_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def role_required(min_role: str):
    """Dependency factory. Usage: Depends(role_required('admin'))

    Role hierarchy: viewer < admin < owner
    """
    roles = ["viewer", "admin", "owner"]

    def _dependency(current_user=Depends(get_current_user)):
        try:
            user_role = current_user.role or "viewer"
            if roles.index(user_role) < roles.index(min_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid role",
            )
        return current_user

    return _dependency
