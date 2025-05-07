"""
API Gateway service to handle routing between Flask and FastAPI components.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Optional, Dict, Any
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Sanctions RAG API Gateway",
    description="API Gateway for routing requests between Flask and FastAPI services",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
FLASK_SERVICE_URL = os.getenv("FLASK_SERVICE_URL", "http://localhost:5000")
FASTAPI_SERVICE_URL = os.getenv("FASTAPI_SERVICE_URL", "http://localhost:8000")

# HTTP client
http_client = None

# Authentication dependency
async def verify_token(request: Request) -> Optional[str]:
    """
    Verify the authentication token.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Optional[str]: User ID if token is valid, None otherwise
    """
    token = request.headers.get("Authorization")
    if not token:
        return None
    
    try:
        # Forward token verification to auth service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLASK_SERVICE_URL}/api/auth/verify",
                headers={"Authorization": token}
            )
            if response.status_code == 200:
                return response.json().get("user_id")
            return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None

# Routes
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Legal Sanctions RAG API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "services": {
            "flask": FLASK_SERVICE_URL,
            "fastapi": FASTAPI_SERVICE_URL
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint for API Gateway and Nginx proxy."""
    return {"status": "ok"}

# RAG Service Routes (FastAPI)
@app.post("/api/query")
async def query_rag(request: Request, user_id: Optional[str] = Depends(verify_token)):
    """
    Query the RAG service.
    
    Args:
        request: FastAPI request object
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to FastAPI service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FASTAPI_SERVICE_URL}/api/query",
                json=await request.json(),
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error querying RAG service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/documents")
async def process_documents(request: Request, user_id: Optional[str] = Depends(verify_token)):
    """
    Process documents through the RAG service.
    
    Args:
        request: FastAPI request object
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to FastAPI service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FASTAPI_SERVICE_URL}/api/documents",
                json=await request.json(),
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Dataset Management Routes (FastAPI)
@app.get("/api/datasets")
async def get_datasets(user_id: Optional[str] = Depends(verify_token)):
    """
    Get available datasets.
    
    Args:
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to FastAPI service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_SERVICE_URL}/api/datasets",
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error getting datasets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/datasets/{dataset_name}")
async def delete_dataset(
    dataset_name: str,
    user_id: Optional[str] = Depends(verify_token)
):
    """
    Delete a dataset.
    
    Args:
        dataset_name: Name of the dataset to delete
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to FastAPI service
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{FASTAPI_SERVICE_URL}/api/datasets/{dataset_name}",
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error deleting dataset: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Chat Service Routes (Flask)
@app.get("/api/chat")
async def get_chats(user_id: Optional[str] = Depends(verify_token)):
    """
    Get user's chat history.
    
    Args:
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to Flask service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FLASK_SERVICE_URL}/api/chat",
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error getting chats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat")
async def create_chat(request: Request, user_id: Optional[str] = Depends(verify_token)):
    """
    Create a new chat.
    
    Args:
        request: FastAPI request object
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to Flask service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLASK_SERVICE_URL}/api/chat",
                json=await request.json(),
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Management Routes (Flask)
@app.get("/api/user")
async def get_user(user_id: Optional[str] = Depends(verify_token)):
    """
    Get user information.
    
    Args:
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to Flask service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FLASK_SERVICE_URL}/api/user",
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/user")
async def create_user(request: Request):
    """
    Create a new user.
    
    Args:
        request: FastAPI request object
    """
    try:
        # Forward request to Flask service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLASK_SERVICE_URL}/api/user",
                json=await request.json()
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Authentication Routes (Flask)
@app.post("/api/login")
async def login(request: Request):
    """
    Authenticate user.
    
    Args:
        request: FastAPI request object
    """
    try:
        # Forward request to Flask service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLASK_SERVICE_URL}/api/login",
                json=await request.json()
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/logout")
async def logout(request: Request, user_id: Optional[str] = Depends(verify_token)):
    """
    Logout user.
    
    Args:
        request: FastAPI request object
        user_id: Optional user ID from token verification
    """
    try:
        # Forward request to Flask service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLASK_SERVICE_URL}/api/logout",
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests and responses.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware function
    """
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Get start time
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log response
    logger.info(f"Response: {response.status_code} ({duration:.2f}s)")
    
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Check service availability on startup.
    """
    try:
        # Check Flask service
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FLASK_SERVICE_URL}/health")
            if response.status_code != 200:
                logger.error("Flask service is not available")
        
        # Check FastAPI service
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FASTAPI_SERVICE_URL}/health")
            if response.status_code != 200:
                logger.error("FastAPI service is not available")
        
        logger.info("API Gateway started successfully")
    
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown.
    """
    try:
        # Close HTTP client
        await http_client.aclose()
        
        logger.info("API Gateway shut down successfully")
    
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}") 