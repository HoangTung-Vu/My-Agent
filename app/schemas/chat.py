from typing import Optional, List
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Model for request send to the chat endpoint.
    """
    message : str
    conversation_id : Optional[str]

class ChatResponse(BaseModel):
    """
    Model for response from the chat endpoint.
    """
    conversation_id : str
    response : str
    sources : Optional[List[str]] = None # List of sources for the response, if applicable