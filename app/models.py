from .database import Base
from sqlalchemy import Column, Integer, LargeBinary, String, ForeignKey, Float
from sqlalchemy.orm import relationship

# Define relationships
from sqlalchemy.sql.expression import text
import time
from pydantic import field_validator

""" I need two tables Market, which will have the ID, name and include many products, and Product, that will belong to one market, product can have duplicate names but different IDs, and will have a price """

class Market(Base):
    __tablename__ = "markets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    products = relationship("Product", back_populates="market")
    created_at = Column(String, index=True, nullable=False, server_default=time.strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String, index=True, nullable=False, server_default=time.strftime("%Y-%m-%d %H:%M:%S"))

    #order by created_at by default
    


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float, nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"))
    market = relationship("Market", back_populates="products")
    created_at = Column(String, index=True, nullable=False, server_default=time.strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String, index=True, nullable=False, server_default=time.strftime("%Y-%m-%d %H:%M:%S"))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    # The role can be 'admin', 'free', or other roles as needed
    role = Column(String, default="free", nullable=False)
    created_at = Column(String, index=True, nullable=False, server_default=time.strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String, index=True, nullable=False, server_default=time.strftime("%Y-%m-%d %H:%M:%S"))

    #Validate role field
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ["admin", "free", "user"]:
            raise ValueError("Role must be either 'admin' or 'free' or 'user'")
        return v


class SessionModel(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String, unique=True, index=True)