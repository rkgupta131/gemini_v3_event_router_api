"""
FastAPI Application - Webpage Builder API
Main entry point for the REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api.routes import (
    intent,
    page_type,
    query,
    chat,
    project,
    events,
    questionnaire,
    categories,
    unified
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Webpage Builder API",
    description="AI-powered webpage builder API using Gemini models",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Unified endpoint (single API for all operations)
app.include_router(unified.router, prefix="/api/v1", tags=["Unified API"])

# Individual endpoints (for backward compatibility)
app.include_router(intent.router, prefix="/api/v1", tags=["Intent"])
app.include_router(page_type.router, prefix="/api/v1", tags=["Page Type"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(project.router, prefix="/api/v1", tags=["Project"])
app.include_router(events.router, prefix="/api/v1", tags=["Events"])
app.include_router(questionnaire.router, prefix="/api/v1", tags=["Questionnaire"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categories"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Webpage Builder API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "webpage-builder-api"
    }

