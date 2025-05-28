from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship
import uuid

class Conversation(Base):
    """
    ORM model for a conversation.
    - Có quan hệ 1-n với Message (một cuộc hội thoại có nhiều tin nhắn).
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """
    ORM model for a message.
    - Mỗi message thuộc về một conversation (quan hệ n-1).
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    conversation = relationship("Conversation", back_populates="messages")