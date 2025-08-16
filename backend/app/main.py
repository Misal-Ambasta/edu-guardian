
"""Main module for the application.

This module provides functionality related to main.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database.db import get_db
from sqlalchemy.orm import Session
from .routers import auth, emotion, reports, interventions, students
import os

app = FastAPI(
    title="Edu-Guardian API",
    description="RAG-Powered Historical Intelligence System with Advanced Emotion Analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(emotion.router, prefix="/api/emotion", tags=["Emotion Analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(interventions.router, prefix="/api/interventions", tags=["Interventions"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "edu-guardian-api"}

@app.get("/")
def root():
    return {
        "message": "Welcome to Edu-Guardian API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
