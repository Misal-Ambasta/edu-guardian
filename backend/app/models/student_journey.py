
"""Student Journey module for the application.

This module provides functionality related to student journey.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..database.db import Base
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# SQLAlchemy Student Journey Model
class StudentJourney(Base):
    __tablename__ = "student_journeys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(String, nullable=False, index=True)
    course_id = Column(String, nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    nps_score = Column(Integer)

    # Aspect scores (1-5 scale)
    lms_usability_score = Column(Integer)
    instructor_quality_score = Column(Integer)
    content_difficulty_score = Column(Integer)
    support_quality_score = Column(Integer)
    course_pace_score = Column(Integer)

    comments = Column(Text)

    # Advanced Emotion Analysis Fields
    frustration_level = Column(Float)
    engagement_level = Column(Float)
    confidence_level = Column(Float)
    satisfaction_level = Column(Float)

    frustration_type = Column(String)  # 'technical', 'content', 'pace', 'support', 'mixed'
    frustration_intensity = Column(String)  # 'mild', 'moderate', 'severe', 'critical'
    frustration_trend = Column(String)  # 'increasing', 'decreasing', 'stable', 'spiking'

    urgency_level = Column(String)  # 'low', 'medium', 'high', 'critical', 'immediate'
    urgency_signals = Column(JSONB)  # Array of urgency indicators
    response_urgency = Column(String)  # 'within_hour', 'same_day', 'within_week', 'routine'

    emotional_temperature = Column(Float)
    emotional_volatility = Column(Float)
    emotional_trajectory = Column(String)  # 'improving', 'declining', 'neutral', 'fluctuating'

    hidden_dissatisfaction_flag = Column(Boolean, default=False)
    hidden_dissatisfaction_confidence = Column(Float)
    hidden_signals = Column(JSONB)  # Array of hidden dissatisfaction indicators
    politeness_mask_level = Column(Float)

    dropout_risk_emotions = Column(JSONB)  # Array of emotions indicating dropout risk
    positive_recovery_indicators = Column(JSONB)  # Array of positive emotional indicators
    emotional_triggers = Column(JSONB)  # What triggers negative emotions

    emotion_coherence = Column(Float)
    sentiment_authenticity = Column(Float)
    emotional_complexity = Column(String)  # 'simple', 'mixed', 'complex', 'conflicted'

    demographic_type = Column(String)
    current_grade = Column(Float)
    attendance_rate = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Add check constraints
    __table_args__ = (
        CheckConstraint('nps_score >= 0 AND nps_score <= 10', name='check_nps_score'),
        CheckConstraint(
            'lms_usability_score >= 1 AND lms_usability_score <= 5', name='check_lms_score'),
        CheckConstraint(
            'instructor_quality_score >= 1 AND instructor_quality_score <= 5', name='check_instructor_score'),
        CheckConstraint(
            'content_difficulty_score >= 1 AND content_difficulty_score <= 5', name='check_content_score'),
        CheckConstraint(
            'support_quality_score >= 1 AND support_quality_score <= 5', name='check_support_score'),
        CheckConstraint(
            'course_pace_score >= 1 AND course_pace_score <= 5', name='check_pace_score'),
        CheckConstraint(
            'frustration_level >= 0 AND frustration_level <= 1', name='check_frustration_level'),
        CheckConstraint(
            'engagement_level >= 0 AND engagement_level <= 1', name='check_engagement_level'),
        CheckConstraint(
            'confidence_level >= 0 AND confidence_level <= 1', name='check_confidence_level'),
        CheckConstraint(
            'satisfaction_level >= 0 AND satisfaction_level <= 1', name='check_satisfaction_level'),
        CheckConstraint(
            'emotional_temperature >= 0 AND emotional_temperature <= 1', name='check_emotional_temp'),
        CheckConstraint(
            'emotional_volatility >= 0 AND emotional_volatility <= 1', name='check_emotional_volatility'),
        CheckConstraint(
            'hidden_dissatisfaction_confidence >= 0 AND hidden_dissatisfaction_confidence <= 1', name='check_hidden_confidence'),
        CheckConstraint(
            'politeness_mask_level >= 0 AND politeness_mask_level <= 1', name='check_politeness_mask'),
        CheckConstraint(
            'emotion_coherence >= 0 AND emotion_coherence <= 1', name='check_emotion_coherence'),
        CheckConstraint(
            'sentiment_authenticity >= 0 AND sentiment_authenticity <= 1', name='check_sentiment_authenticity'),
    )

# Pydantic Models for API
class StudentJourneyBase(BaseModel):
    student_id: str
    course_id: str
    week_number: int
    nps_score: Optional[int] = Field(None, ge=0, le=10)

    # Aspect scores
    lms_usability_score: Optional[int] = Field(None, ge=1, le=5)
    instructor_quality_score: Optional[int] = Field(None, ge=1, le=5)
    content_difficulty_score: Optional[int] = Field(None, ge=1, le=5)
    support_quality_score: Optional[int] = Field(None, ge=1, le=5)
    course_pace_score: Optional[int] = Field(None, ge=1, le=5)

    comments: Optional[str] = None

class StudentJourneyCreate(StudentJourneyBase):
    # Advanced emotion fields
    frustration_level: Optional[float] = Field(None, ge=0, le=1)
    engagement_level: Optional[float] = Field(None, ge=0, le=1)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    satisfaction_level: Optional[float] = Field(None, ge=0, le=1)

    frustration_type: Optional[str] = None
    frustration_intensity: Optional[str] = None
    frustration_trend: Optional[str] = None

    urgency_level: Optional[str] = None
    urgency_signals: Optional[List[str]] = None
    response_urgency: Optional[str] = None

    emotional_temperature: Optional[float] = Field(None, ge=0, le=1)
    emotional_volatility: Optional[float] = Field(None, ge=0, le=1)
    emotional_trajectory: Optional[str] = None

    hidden_dissatisfaction_flag: Optional[bool] = False
    hidden_dissatisfaction_confidence: Optional[float] = Field(None, ge=0, le=1)
    hidden_signals: Optional[List[str]] = None
    politeness_mask_level: Optional[float] = Field(None, ge=0, le=1)

    dropout_risk_emotions: Optional[List[str]] = None
    positive_recovery_indicators: Optional[List[str]] = None
    emotional_triggers: Optional[List[str]] = None

    emotion_coherence: Optional[float] = Field(None, ge=0, le=1)
    sentiment_authenticity: Optional[float] = Field(None, ge=0, le=1)
    emotional_complexity: Optional[str] = None

    demographic_type: Optional[str] = None
    current_grade: Optional[float] = None
    attendance_rate: Optional[float] = None

class StudentJourneyUpdate(StudentJourneyCreate):
    pass

class StudentJourneyInDB(StudentJourneyBase):
    id: uuid.UUID
    timestamp: datetime

    # Include all advanced emotion fields
    frustration_level: Optional[float] = None
    engagement_level: Optional[float] = None
    confidence_level: Optional[float] = None
    satisfaction_level: Optional[float] = None

    frustration_type: Optional[str] = None
    frustration_intensity: Optional[str] = None
    frustration_trend: Optional[str] = None

    urgency_level: Optional[str] = None
    urgency_signals: Optional[List[str]] = None
    response_urgency: Optional[str] = None

    emotional_temperature: Optional[float] = None
    emotional_volatility: Optional[float] = None
    emotional_trajectory: Optional[str] = None

    hidden_dissatisfaction_flag: Optional[bool] = False
    hidden_dissatisfaction_confidence: Optional[float] = None
    hidden_signals: Optional[List[str]] = None
    politeness_mask_level: Optional[float] = None

    dropout_risk_emotions: Optional[List[str]] = None
    positive_recovery_indicators: Optional[List[str]] = None
    emotional_triggers: Optional[List[str]] = None

    emotion_coherence: Optional[float] = None
    sentiment_authenticity: Optional[float] = None
    emotional_complexity: Optional[str] = None

    demographic_type: Optional[str] = None
    current_grade: Optional[float] = None
    attendance_rate: Optional[float] = None

    class Config:
        from_attributes = True
