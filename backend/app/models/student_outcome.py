
"""Student Outcome module for the application.

This module provides functionality related to student outcome.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..database.db import Base
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# SQLAlchemy Student Outcome Model
class StudentOutcome(Base):
    __tablename__ = "student_outcomes"

    student_id = Column(String, primary_key=True)
    course_id = Column(String, nullable=False, index=True)
    completion_status = Column(
        String, nullable=False)  # 'completed', 'dropped_week_X', 'transferred'
    final_grade = Column(Float)
    job_placement_status = Column(String)  # 'placed', 'not_placed', 'unknown'
    time_to_placement_days = Column(Integer)
    final_nps_score = Column(Integer)

    # Emotion Journey Summary
    emotion_journey_summary = Column(JSONB)  # Key emotional milestones
    final_emotion_state = Column(JSONB)  # Final emotional profile
    emotional_recovery_success = Column(Boolean)  # Did emotional interventions work

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Models for API
class StudentOutcomeBase(BaseModel):
    student_id: str
    course_id: str
    completion_status: str

class StudentOutcomeCreate(StudentOutcomeBase):
    final_grade: Optional[float] = None
    job_placement_status: Optional[str] = None
    time_to_placement_days: Optional[int] = None
    final_nps_score: Optional[int] = Field(None, ge=0, le=10)

    # Emotion Journey Summary
    emotion_journey_summary: Optional[Dict[str, Any]] = None
    final_emotion_state: Optional[Dict[str, Any]] = None
    emotional_recovery_success: Optional[bool] = None

class StudentOutcomeUpdate(BaseModel):
    completion_status: Optional[str] = None
    final_grade: Optional[float] = None
    job_placement_status: Optional[str] = None
    time_to_placement_days: Optional[int] = None
    final_nps_score: Optional[int] = Field(None, ge=0, le=10)

    # Emotion Journey Summary
    emotion_journey_summary: Optional[Dict[str, Any]] = None
    final_emotion_state: Optional[Dict[str, Any]] = None
    emotional_recovery_success: Optional[bool] = None

class StudentOutcomeInDB(StudentOutcomeBase):
    final_grade: Optional[float] = None
    job_placement_status: Optional[str] = None
    time_to_placement_days: Optional[int] = None
    final_nps_score: Optional[int] = None

    # Emotion Journey Summary
    emotion_journey_summary: Optional[Dict[str, Any]] = None
    final_emotion_state: Optional[Dict[str, Any]] = None
    emotional_recovery_success: Optional[bool] = None

    created_at: datetime

    class Config:
        from_attributes = True
