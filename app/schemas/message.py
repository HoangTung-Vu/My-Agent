from typing import Optional 
from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    """
    Model for a message in a conversation.
    """
    id : Optional[int] = None
    conversation_id : str
    role : str  
    content : str
    timestamp : datetime 

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models


class Conversation(BaseModel):
    """
    Model for a conversation.
    """
    id : Optional[str] = None  
    system_prompt : Optional[str] = None  
    created_at : datetime
    updated_at : datetime

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models