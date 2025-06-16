from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class LicenseInfo(BaseModel):
    license_type: str
    issued_at: datetime
    expires_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LicenseCheck(BaseModel):
    username: str
    uuid: str