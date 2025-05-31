from sqlalchemy.orm import Session as DBSession
from app.models.orm import Message, Session  # Use ORM models instead of Pydantic models

def create_session(db: DBSession):
    """
    Create a new session in the database and return its ID.
    """
    session = Session()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.id

def add_message_to_session(db: DBSession, session_id: str, role: str, content: str):
    """
    Add a message to a session in the database.
    """
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_session_messages(db: DBSession, session_id: str):
    """
    Get all messages for a session from the database, sorted by timestamp (oldest first).
    """
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp.asc()).all()


def get_all_sessions(db: DBSession, skip: int = 0, limit: int = 100):
    """
    Get all sessions from the database, sorted by updated_at (newest first).
    """
    return db.query(Session).order_by(Session.updated_at.desc()).offset(skip).limit(limit).all()


def delete_session(db: DBSession, session_id: str):
    """
    Delete a session and all its messages from the database.
    Returns True if successful, False if the session was not found.
    """
    # Messages will be deleted automatically due to cascade="all, delete-orphan"
    # db.query(Message).filter(Message.session_id == session_id).delete() 
    result = db.query(Session).filter(Session.id == session_id).delete()
    db.commit()
    
    return result > 0  # Returns True if at least one row was deleted


def get_session(db: DBSession, session_id: str):
    """
    Get a specific session by ID.
    """
    return db.query(Session).filter(Session.id == session_id).first()