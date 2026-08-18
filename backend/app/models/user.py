import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Boolean
from app.db.base import Base
from app.db.types import UUIDType


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    DATA_OPERATOR = "DATA_OPERATOR"


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    anonymous_id = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
