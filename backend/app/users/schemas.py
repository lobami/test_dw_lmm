from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    email: str
    password: str
    company_name: Optional[str] = None


class OwnerCreateUser(BaseModel):
    email: str
    password: str
    role: Optional[str] = "viewer"


class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    company_id: Optional[int] = None
    role: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
