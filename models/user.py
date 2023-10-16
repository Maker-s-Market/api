import uuid
import datetime
import enum
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, Enum

from db.database import Base


class Role(enum.Enum):
    Admin = "Admin"
    Client = "Client"
    Premium = "Premium"


class User(Base):
    __tablename__ = "user"

    #Change to UUID
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(Enum(Role))  # Ver se isto dá certo ou não
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)

    # POR CAUSA DO RGPD
    deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    is_active = Column(Integer, index=True, default=1, nullable=False)

    #! Falta FollowING and Followers