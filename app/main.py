from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os

from app.api.chat_router import router as chat_router
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent Chatbot",
    description="API for interacting with AI agent chatbot",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

frontend_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_folder), name="frontend")

@app.get("/")
async def redirect_to_frontend():
    # Redirect directly to the frontend UI
    return RedirectResponse(url="/frontend/index.html")