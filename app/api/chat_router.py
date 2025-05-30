from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.message import Message, Conversation
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db.crud import create_conversation, add_message_to_conversation, get_conversation_messages, get_all_conversations, delete_conversation
from app.core.main_agent import process_message

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a chat message and return the agent's response.
    Creates a new conversation if conversation_id is not provided.
    """
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = create_conversation(db)
    
    # Store user message
    add_message_to_conversation(db, conversation_id, "user", request.message)
    response, sources = await process_message(request.message, conversation_id)
    add_message_to_conversation(db, conversation_id, "assistant", response)
    
    return ChatResponse(
        conversation_id=conversation_id,
        response=response,
        sources=sources
    )

@router.get("/conversations/{conversation_id}", response_model=List[Message])
async def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the message history for a specific conversation.
    """
    messages = get_conversation_messages(db, conversation_id)
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    return messages

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all conversations, sorted by most recent first.
    """
    conversations = get_all_conversations(db, skip=skip, limit=limit)
    return conversations

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Delete a conversation and all its messages.
    """
    success = delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return None
