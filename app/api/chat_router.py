from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.message import Message, Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db.crud import create_session, add_message_to_session, get_session_messages, get_all_sessions, delete_session
from app.core.main_agent import process_message

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest, db: DBSession = Depends(get_db)):
    """
    Process a chat message and return the agent's response.
    Creates a new session if session_id is not provided.
    """
    session_id = request.session_id
    if not session_id:
        session_id = create_session(db)
    
    # Store user message
    add_message_to_session(db, session_id, "user", request.message)
    response, sources = await process_message(request.message, session_id)
    add_message_to_session(db, session_id, "assistant", response)
    
    return ChatResponse(
        session_id=session_id,
        response=response,
        sources=sources
    )

@router.get("/sessions/{session_id}", response_model=List[Message])
async def get_session_history(session_id: str, db: DBSession = Depends(get_db)):
    """
    Retrieve the message history for a specific session.
    """
    messages = get_session_messages(db, session_id)
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    return messages

@router.get("/sessions", response_model=List[Session])
async def get_sessions(skip: int = 0, limit: int = 100, db: DBSession = Depends(get_db)):
    """
    Retrieve all sessions, sorted by most recent first.
    """
    sessions = get_all_sessions(db, skip=skip, limit=limit)
    return sessions

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_session(session_id: str, db: DBSession = Depends(get_db)):
    """
    Delete a session and all its messages.
    """
    success = delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    return None
