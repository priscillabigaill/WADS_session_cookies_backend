from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    items = relationship("Item", back_populates="owner")
    sessions = relationship("Session", back_populates="user")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_completed = Column(Boolean, default=False)  # Use "is_completed" instead of "completed"

    owner = relationship("User", back_populates="items")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Define a relationship with the User model
    user = relationship("User", back_populates="sessions")  
