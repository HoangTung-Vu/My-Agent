from sqlalchemy.orm import Session
from app.models.orm import Message, Conversation  # Use ORM models instead of Pydantic models

def create_conversation(db: Session):
    """
    Create a new conversation in the database and return its ID.
    """
    conversation = Conversation()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation.id

def add_message_to_conversation(db: Session, conversation_id: str, role: str, content: str):
    """
    Add a message to a conversation in the database.
    """
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_conversation_messages(db: Session, conversation_id: str):
    """
    Get all messages for a conversation from the database, sorted by timestamp (oldest first).
    """
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc()).all()


def get_all_conversations(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all conversations from the database, sorted by updated_at (newest first).
    """
    return db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()


def delete_conversation(db: Session, conversation_id: str):
    """
    Delete a conversation and all its messages from the database.
    Returns True if successful, False if the conversation was not found.
    """
    # Messages will be deleted automatically due to cascade="all, delete-orphan"
    # db.query(Message).filter(Message.conversation_id == conversation_id).delete() 
    result = db.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db.commit()
    
    return result > 0  # Returns True if at least one row was deleted


def get_conversation(db: Session, conversation_id: str):
    """
    Get a specific conversation by ID.
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()