from typing import Optional
from datetime import datetime
from app.schemas.compat import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    state: Optional[str] = "Telangana"
    city: Optional[str] = "Hyderabad"
    utility: Optional[str] = "TGSPDCL"
    tariff_category: Optional[str] = "LT-I(A)"
    consent_granted: bool = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    state: str
    city: str
    utility: str
    tariff_category: str
    created_at: datetime
    current_tariff_category: Optional[str] = None
    current_utility: Optional[str] = None
    
    class Config:
        from_attributes = True
