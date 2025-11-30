"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, bots, training, chat, conversations, training_jobs

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chatbot Management Platform API",
    description="API for managing chatbots and training data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Register training_jobs before bots to avoid route conflicts
# (more specific /bots/{bot_id}/train must come before generic /bots/{bot_id})
app.include_router(auth.router, prefix="/api")
app.include_router(training_jobs.router, prefix="/api")
app.include_router(bots.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Chatbot Management Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
