from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship
import uuid

class Session(Base):
    """
    ORM model for a session.
    - Có quan hệ 1-n với Message (một phiên có nhiều tin nhắn).
    """
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), index=True) # Add index here
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    """
    ORM model for a message.
    - Mỗi message thuộc về một session (quan hệ n-1).
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    session = relationship("Session", back_populates="messages")

    __table_args__ = (
        Index('ix_messages_session_id_timestamp', "session_id", "timestamp"),
    )