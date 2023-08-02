from pydantic import BaseModel
from database import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password = Column(String)


class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    count = Column(Integer)
    cost = Column(Integer)


class UserRequest(BaseModel):
    email: str
    full_name: str
    password: str
    id: int | None

class FlowerRequest(BaseModel):
    name: str
    count: int
    cost: int

