from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.memory.user_assisstant_memory import get_or_create_ua_collection

DATABASE_URL = "sqlite:///./data/database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Create the database tables if they do not exist.
    Create the user and assistant memory collections in ChromaDB if not exist.
    """
    Base.metadata.create_all(bind=engine)
    get_or_create_ua_collection() 
    print("Database initialized and tables created.")

