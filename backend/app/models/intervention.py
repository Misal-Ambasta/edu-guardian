
"""Intervention module for the application.

This module provides functionality related to intervention.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..database.db import Base
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# SQLAlchemy Intervention Model
class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(String, nullable=False, index=True)
    intervention_type = Column(String, nullable=False)  # 'lms_walkthrough', 'mentor_assigned', etc.
    target_aspect = Column(String)  # 'lms_usability', 'instructor_quality', etc.

    # Emotion-based targeting
    target_emotion = Column(String)  # 'frustration', 'hidden_dissatisfaction', etc.
    emotional_urgency_level = Column(String)
    intervention_urgency = Column(String)  # How quickly intervention was applied

    recommended_week = Column(Integer)
    applied_week = Column(Integer)
    intervention_details = Column(JSONB)  # Template used, resources provided, etc.

    # Enhanced outcome tracking
    success_metrics = Column(JSONB)  # Before/after scores, completion status
    emotion_improvement = Column(JSONB)  # Before/after emotional states
    outcome_status = Column(String)  # 'successful', 'failed', 'partial'

    # Timing analysis
    response_time_hours = Column(Float)  # How quickly we responded to urgent signals
    intervention_to_improvement_days = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Models for API
class InterventionBase(BaseModel):
    student_id: str
    intervention_type: str

class InterventionCreate(InterventionBase):
    target_aspect: Optional[str] = None

    # Emotion-based targeting
    target_emotion: Optional[str] = None
    emotional_urgency_level: Optional[str] = None
    intervention_urgency: Optional[str] = None

    recommended_week: Optional[int] = None
    applied_week: Optional[int] = None
    intervention_details: Optional[Dict[str, Any]] = None

    # Enhanced outcome tracking
    success_metrics: Optional[Dict[str, Any]] = None
    emotion_improvement: Optional[Dict[str, Any]] = None
    outcome_status: Optional[str] = None

    # Timing analysis
    response_time_hours: Optional[float] = None
    intervention_to_improvement_days: Optional[int] = None

class InterventionUpdate(BaseModel):
    intervention_type: Optional[str] = None
    target_aspect: Optional[str] = None

    # Emotion-based targeting
    target_emotion: Optional[str] = None
    emotional_urgency_level: Optional[str] = None
    intervention_urgency: Optional[str] = None

    recommended_week: Optional[int] = None
    applied_week: Optional[int] = None
    intervention_details: Optional[Dict[str, Any]] = None

    # Enhanced outcome tracking
    success_metrics: Optional[Dict[str, Any]] = None
    emotion_improvement: Optional[Dict[str, Any]] = None
    outcome_status: Optional[str] = None

    # Timing analysis
    response_time_hours: Optional[float] = None
    intervention_to_improvement_days: Optional[int] = None

class InterventionInDB(InterventionBase):
    id: uuid.UUID
    target_aspect: Optional[str] = None

    # Emotion-based targeting
    target_emotion: Optional[str] = None
    emotional_urgency_level: Optional[str] = None
    intervention_urgency: Optional[str] = None

    recommended_week: Optional[int] = None
    applied_week: Optional[int] = None
    intervention_details: Optional[Dict[str, Any]] = None

    # Enhanced outcome tracking
    success_metrics: Optional[Dict[str, Any]] = None
    emotion_improvement: Optional[Dict[str, Any]] = None
    outcome_status: Optional[str] = None

    # Timing analysis
    response_time_hours: Optional[float] = None
    intervention_to_improvement_days: Optional[int] = None

    created_at: datetime

    class Config:
        from_attributes = True
