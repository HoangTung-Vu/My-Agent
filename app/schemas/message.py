from typing import Optional 
from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    """
    Model for a message in a session.
    """
    id : Optional[int] = None
    session_id : str
    role : str  
    content : str
    timestamp : datetime 

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models


class Session(BaseModel):
    """
    Model for a session.
    """
    id : Optional[str] = None  
    system_prompt : Optional[str] = None  
    created_at : datetime
    updated_at : datetime

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models