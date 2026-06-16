from sqlalchemy import Column, Integer, String, Text, DateTime, func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(128))

class QARecord(Base):
    __tablename__ = "qa_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    question = Column(Text)
    answer = Column(Text)
    risk_level = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

class InspectionRecord(Base):
    __tablename__ = "inspection_records"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100))
    inspector = Column(String(50))
    hazard_description = Column(Text)
    risk_level = Column(String(20))
    status = Column(String(20), default="未整改")
    responsible_person = Column(String(50))
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())