from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    username = Column(String(64), primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid4()), nullable=False)
    password_hash = Column(String(256), nullable=False)
    has_active_license = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    licenses = relationship("License", back_populates="user")

class License(Base):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), ForeignKey("users.username"), nullable=False)
    license_type = Column(String(32), default="trial", nullable=False)
    issued_at = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    user = relationship("User", back_populates="licenses")

class LoginLog(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), ForeignKey("users.username"), nullable=False)
    login_time = Column(DateTime, default=datetime.now, nullable=False)
    ip_address = Column(String(45))
