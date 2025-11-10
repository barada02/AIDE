"""
FastAPI application for serving the Brad Pitt ADK agent via REST API.
"""

import logging
from typing import Optional
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from agent_runner import AgentRunner 
from manager.agent import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent runner instance
agent_runner: Optional[AgentRunner] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup/shutdown."""
    global agent_runner
    
    # Startup
    logger.info("Starting Brad Pitt Agent API...")
    agent_runner = AgentRunner(
        agent=root_agent,
        app_name="bradPittAPI",
        user_id="api_user"
    )
    logger.info("Agent runner initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Brad Pitt Agent API...")


# Create FastAPI app
app = FastAPI(
    title="Brad Pitt Agent API",
    description="Chat with Brad Pitt using Google ADK",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User's message/question for Brad Pitt")
    user_id: str = Field(default="default_user", description="Unique identifier for the user")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Brad Pitt's response")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(default="success", description="Response status")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    status: str = Field(default="error", description="Error status")


class SessionInfo(BaseModel):
    user_id: str
    active_sessions: list[str]
    total_sessions: int


# API Endpoints

@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Brad Pitt Agent API",
        "version": "1.0.0",
        "description": "Chat with Brad Pitt using Google ADK",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "sessions": "/sessions/{user_id}"
        }
    }


@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": "Brad Pitt Agent",
        "service": "running"
    }


@app.post("/chat", response_model=ChatResponse, summary="Chat with Brad Pitt")
async def chat_with_brad(request: ChatRequest) -> ChatResponse:
    """
    Send a message to Brad Pitt and get his response.
    
    - **prompt**: Your message or question for Brad Pitt
    - **user_id**: Your unique user identifier (optional)
    - **session_id**: Session ID for conversation continuity (optional, auto-generated if not provided)
    """
    global agent_runner
    
    if not agent_runner:
        raise HTTPException(status_code=503, detail="Agent runner not initialized")
    
    try:
        logger.info(f"Chat request from user {request.user_id}: {request.prompt}")
        
        # Run the agent with user's prompt
        response = await agent_runner.run_agent(
            prompt=request.prompt,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Get the actual session ID (in case it was auto-generated)
        session_id = request.session_id
        if session_id is None:
            # If no session_id provided, it would have been auto-generated
            session_id = f"session_{request.user_id}_1"
        
        return ChatResponse(
            response=response,
            user_id=request.user_id,
            session_id=session_id,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat request: {str(e)}"
        )


@app.get("/sessions/{user_id}", response_model=SessionInfo, summary="Get user session info")
async def get_user_sessions(user_id: str) -> SessionInfo:
    """
    Get information about a user's active sessions.
    
    - **user_id**: The user identifier to get session info for
    """
    global agent_runner
    
    if not agent_runner:
        raise HTTPException(status_code=503, detail="Agent runner not initialized")
    
    try:
        session_info = await agent_runner.get_session_info(user_id)
        return SessionInfo(**session_info)
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )


@app.delete("/sessions/{user_id}/{session_id}", summary="Delete a session")
async def delete_session(user_id: str, session_id: str):
    """
    Delete a specific user session.
    
    - **user_id**: The user identifier
    - **session_id**: The session identifier to delete
    """
    # This would require implementing session deletion in AgentRunner
    # For now, return a placeholder response
    return {
        "message": f"Session deletion requested for user {user_id}, session {session_id}",
        "note": "Session deletion not yet implemented"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {
        "error": exc.detail,
        "status": "error",
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "status": "error",
        "status_code": 500
    }


# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",  # Changed from 0.0.0.0 to localhost
        port=8080,
        reload=True,
        log_level="info"
    )