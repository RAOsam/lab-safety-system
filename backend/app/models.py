from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .database import Base

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100))
    lab_name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    role = Column(String(20), default=UserRole.USER.value)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    qa_records = relationship("QARecord", back_populates="user")
    inspection_records = relationship("InspectionRecord", back_populates="inspector_user")
    feedbacks = relationship("Feedback", back_populates="user", foreign_keys="Feedback.user_id")

class QARecord(Base):
    __tablename__ = "qa_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    risk_level = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="qa_records")

class InspectionRecord(Base):
    __tablename__ = "inspection_records"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100))
    inspector_id = Column(Integer, ForeignKey("users.id"))
    inspector = Column(String(50))
    hazard_description = Column(Text)
    risk_level = Column(String(20))
    status = Column(String(20), default="待整改")  # 待整改、整改中、已验收
    responsible_person = Column(String(50))
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    inspector_user = relationship("User", back_populates="inspection_records")

class HazardTracking(Base):
    __tablename__ = "hazard_tracking"
    id = Column(Integer, primary_key=True, index=True)
    qa_record_id = Column(Integer, ForeignKey("qa_records.id"), index=True)
    location = Column(String(100))
    hazard_type = Column(String(100))
    risk_level = Column(String(20))
    description = Column(Text)
    status = Column(String(20), default="待整改")  # 待整改、整改中、已验收、已关闭
    responsible_person = Column(String(50))
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    evidence_image = Column(String(255))  # 证据图片路径
    remarks = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    qa_record = relationship("QARecord")

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    qa_record_id = Column(Integer, ForeignKey("qa_records.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # 1-5星评分
    comment = Column(Text)
    is_correct = Column(Integer, default=None)  # 1: 正确, 0: 不正确, None: 未审核
    admin_reply = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    qa_record = relationship("QARecord")
    user = relationship("User", back_populates="feedbacks", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20))  # txt, pdf, docx
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    category = Column(String(100))  # 规章制度、MSDS、事故案例、应急处置等
    description = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Integer, default=1)  # 1: 启用, 0: 禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    uploader = relationship("User")