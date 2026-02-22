


from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime



class MarketBase(BaseModel):
    id: Optional[int] = None
    name: str
    updated_at: Optional[str] = None
    created_at: Optional[str] = None

class CreateMarket(MarketBase):
    pass


class UpdateMarket(MarketBase):
    pass


class MarketResponse(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    market: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    pass

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    market_name: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: EmailStr
    password: str
    created_at: Optional[str] = None
    role: str

class UserCreate(UserBase):
    pass

    @validator('role')
    def validate_role(cls, v):
        if v not in ["admin", "free", "user"]:
            raise ValueError("Role must be either 'admin', 'free', or 'user'")
        return v


class UserLogin(BaseModel):
    username: EmailStr
    password: str

class UserUpdate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    username: EmailStr
    created_at: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None