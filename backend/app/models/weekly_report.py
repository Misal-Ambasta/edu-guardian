
"""Weekly Report module for the application.

This module provides functionality related to weekly report.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..database.db import Base
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# SQLAlchemy Weekly NPS Report Model
class WeeklyNPSReport(Base):
    __tablename__ = "weekly_nps_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(String, nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    report_date = Column(Date, nullable=False)

    # Core NPS Metrics
    overall_nps = Column(Float, nullable=False)
    nps_trend = Column(Float)  # Change from previous week
    response_rate = Column(Float)
    total_responses = Column(Integer)

    # Aspect Performance
    aspect_scores = Column(JSONB, nullable=False)  # All 5 aspect averages
    aspect_trends = Column(JSONB)  # Week-over-week changes
    critical_aspects = Column(JSONB)  # Aspects scoring below threshold

    # Emotion Intelligence
    average_frustration_level = Column(Float)
    frustration_distribution = Column(JSONB)  # Count by frustration_type
    urgency_distribution = Column(JSONB)  # Count by urgency_level
    emotional_temperature_avg = Column(Float)
    hidden_dissatisfaction_count = Column(Integer)
    hidden_dissatisfaction_rate = Column(Float)

    # Risk Analysis
    high_risk_students = Column(Integer)
    critical_risk_students = Column(Integer)
    dropout_prediction_summary = Column(JSONB)
    intervention_candidates = Column(Integer)

    # Historical Comparison
    similar_historical_periods = Column(JSONB)  # References to similar past periods
    historical_pattern_match_confidence = Column(Float)
    predicted_outcomes = Column(JSONB)  # Based on historical patterns

    # Intervention Tracking
    interventions_applied = Column(Integer)
    intervention_success_rate = Column(Float)
    intervention_types_used = Column(JSONB)
    pending_interventions = Column(Integer)



    # Report Metadata
    report_confidence = Column(Float)  # Overall confidence in report accuracy
    data_quality_score = Column(Float)  # Quality of underlying data
    recommendations = Column(JSONB)  # Structured recommendations
    executive_summary = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        CheckConstraint('overall_nps >= 0 AND overall_nps <= 10', name='check_overall_nps'),
        CheckConstraint('response_rate >= 0 AND response_rate <= 1', name='check_response_rate'),
        CheckConstraint(
            'average_frustration_level >= 0 AND average_frustration_level <= 1', name='check_avg_frustration'),
        CheckConstraint(
            'emotional_temperature_avg >= 0 AND emotional_temperature_avg <= 1', name='check_emotional_temp_avg'),
        CheckConstraint(
            'hidden_dissatisfaction_rate >= 0 AND hidden_dissatisfaction_rate <= 1', name='check_hidden_rate'),
        CheckConstraint(
            'historical_pattern_match_confidence >= 0 AND historical_pattern_match_confidence <= 1', name='check_pattern_confidence'),
        CheckConstraint(
            'intervention_success_rate >= 0 AND intervention_success_rate <= 1', name='check_intervention_rate'),
        CheckConstraint(
            'report_confidence >= 0 AND report_confidence <= 1', name='check_report_confidence'),
        CheckConstraint(
            'data_quality_score >= 0 AND data_quality_score <= 1', name='check_data_quality'),
    )

# Pydantic Models for API
class WeeklyNPSReportBase(BaseModel):
    course_id: str
    week_number: int
    report_date: date
    overall_nps: float = Field(..., ge=0, le=10)

    # Required fields
    aspect_scores: Dict[str, float]

class WeeklyNPSReportCreate(WeeklyNPSReportBase):
    # Optional fields
    nps_trend: Optional[float] = None
    response_rate: Optional[float] = Field(None, ge=0, le=1)
    total_responses: Optional[int] = None

    aspect_trends: Optional[Dict[str, float]] = None
    critical_aspects: Optional[List[str]] = None

    # Emotion Intelligence
    average_frustration_level: Optional[float] = Field(None, ge=0, le=1)
    frustration_distribution: Optional[Dict[str, int]] = None
    urgency_distribution: Optional[Dict[str, int]] = None
    emotional_temperature_avg: Optional[float] = Field(None, ge=0, le=1)
    hidden_dissatisfaction_count: Optional[int] = None
    hidden_dissatisfaction_rate: Optional[float] = Field(None, ge=0, le=1)

    # Risk Analysis
    high_risk_students: Optional[int] = None
    critical_risk_students: Optional[int] = None
    dropout_prediction_summary: Optional[Dict[str, Any]] = None
    intervention_candidates: Optional[int] = None

    # Historical Comparison
    similar_historical_periods: Optional[List[str]] = None
    historical_pattern_match_confidence: Optional[float] = Field(None, ge=0, le=1)
    predicted_outcomes: Optional[Dict[str, Any]] = None

    # Intervention Tracking
    interventions_applied: Optional[int] = None
    intervention_success_rate: Optional[float] = Field(None, ge=0, le=1)
    intervention_types_used: Optional[Dict[str, int]] = None
    pending_interventions: Optional[int] = None



    # Report Metadata
    report_confidence: Optional[float] = Field(None, ge=0, le=1)
    data_quality_score: Optional[float] = Field(None, ge=0, le=1)
    recommendations: Optional[List[Dict[str, Any]]] = None
    executive_summary: Optional[str] = None

class WeeklyNPSReportUpdate(BaseModel):
    # All fields are optional for updates
    overall_nps: Optional[float] = Field(None, ge=0, le=10)
    nps_trend: Optional[float] = None
    response_rate: Optional[float] = Field(None, ge=0, le=1)
    total_responses: Optional[int] = None

    aspect_scores: Optional[Dict[str, float]] = None
    aspect_trends: Optional[Dict[str, float]] = None
    critical_aspects: Optional[List[str]] = None

    # Emotion Intelligence
    average_frustration_level: Optional[float] = Field(None, ge=0, le=1)
    frustration_distribution: Optional[Dict[str, int]] = None
    urgency_distribution: Optional[Dict[str, int]] = None
    emotional_temperature_avg: Optional[float] = Field(None, ge=0, le=1)
    hidden_dissatisfaction_count: Optional[int] = None
    hidden_dissatisfaction_rate: Optional[float] = Field(None, ge=0, le=1)

    # Risk Analysis
    high_risk_students: Optional[int] = None
    critical_risk_students: Optional[int] = None
    dropout_prediction_summary: Optional[Dict[str, Any]] = None
    intervention_candidates: Optional[int] = None

    # Historical Comparison
    similar_historical_periods: Optional[List[str]] = None
    historical_pattern_match_confidence: Optional[float] = Field(None, ge=0, le=1)
    predicted_outcomes: Optional[Dict[str, Any]] = None

    # Intervention Tracking
    interventions_applied: Optional[int] = None
    intervention_success_rate: Optional[float] = Field(None, ge=0, le=1)
    intervention_types_used: Optional[Dict[str, int]] = None
    pending_interventions: Optional[int] = None



    # Report Metadata
    report_confidence: Optional[float] = Field(None, ge=0, le=1)
    data_quality_score: Optional[float] = Field(None, ge=0, le=1)
    recommendations: Optional[List[Dict[str, Any]]] = None
    executive_summary: Optional[str] = None

class WeeklyNPSReportInDB(WeeklyNPSReportBase):
    id: uuid.UUID

    # Include all fields that might be returned
    nps_trend: Optional[float] = None
    response_rate: Optional[float] = None
    total_responses: Optional[int] = None

    aspect_trends: Optional[Dict[str, float]] = None
    critical_aspects: Optional[List[str]] = None

    # Emotion Intelligence
    average_frustration_level: Optional[float] = None
    frustration_distribution: Optional[Dict[str, int]] = None
    urgency_distribution: Optional[Dict[str, int]] = None
    emotional_temperature_avg: Optional[float] = None
    hidden_dissatisfaction_count: Optional[int] = None
    hidden_dissatisfaction_rate: Optional[float] = None

    # Risk Analysis
    high_risk_students: Optional[int] = None
    critical_risk_students: Optional[int] = None
    dropout_prediction_summary: Optional[Dict[str, Any]] = None
    intervention_candidates: Optional[int] = None

    # Historical Comparison
    similar_historical_periods: Optional[List[str]] = None
    historical_pattern_match_confidence: Optional[float] = None
    predicted_outcomes: Optional[Dict[str, Any]] = None

    # Intervention Tracking
    interventions_applied: Optional[int] = None
    intervention_success_rate: Optional[float] = None
    intervention_types_used: Optional[Dict[str, int]] = None
    pending_interventions: Optional[int] = None



    # Report Metadata
    report_confidence: Optional[float] = None
    data_quality_score: Optional[float] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    executive_summary: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
