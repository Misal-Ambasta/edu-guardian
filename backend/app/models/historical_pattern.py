
"""Historical Pattern module for the application.

This module provides functionality related to historical pattern.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
import uuid
from ..database.db import Base
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from ..emotion_analysis.analyzer import EmotionProfile
from langchain_core.documents import Document

# SQLAlchemy Historical Pattern Model
class HistoricalPattern(Base):
    __tablename__ = "historical_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern_name = Column(String, nullable=False)
    pattern_type = Column(String, nullable=False)  # 'emotional', 'behavioral', 'academic'

    # Pattern definition
    detection_rules = Column(
        JSONB, nullable=False)  # Vector embedding match criteria, keyword patterns
    confidence_threshold = Column(Float)  # How confident we need to be to trigger

    # Emotion intelligence metrics
    emotion_signatures = Column(JSONB)  # Specific emotional patterns this tracks
    early_warning_indicators = Column(ARRAY(String))  # Keywords/signals that are early warnings

    # Efficacy tracking
    success_rate = Column(Float)  # How often interventions for this pattern succeeded
    false_positive_rate = Column(Float)
    avg_detection_week = Column(Float)  # At what point in courses this typically appears

    # Risk assessment
    business_impact = Column(String)  # 'high', 'medium', 'low'
    student_impact = Column(String)  # 'high', 'medium', 'low'
    typical_outcome = Column(String)  # 'dropout', 'completion_with_issues', etc.

    # Intervention efficacy
    recommended_interventions = Column(JSONB)  # Ordered list of interventions that work
    avg_intervention_efficacy = Column(Float)  # How well interventions work on average

    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Models for API
class HistoricalPatternBase(BaseModel):
    pattern_name: str
    pattern_type: str
    detection_rules: Dict[str, Any]

class HistoricalPatternCreate(HistoricalPatternBase):
    confidence_threshold: Optional[float] = None

    # Emotion intelligence metrics
    emotion_signatures: Optional[Dict[str, Any]] = None
    early_warning_indicators: Optional[List[str]] = None

    # Efficacy tracking
    success_rate: Optional[float] = None
    false_positive_rate: Optional[float] = None
    avg_detection_week: Optional[float] = None

    # Risk assessment
    business_impact: Optional[str] = None
    student_impact: Optional[str] = None
    typical_outcome: Optional[str] = None

    # Intervention efficacy
    recommended_interventions: Optional[Dict[str, Any]] = None
    avg_intervention_efficacy: Optional[float] = None

    description: Optional[str] = None

class HistoricalPatternUpdate(BaseModel):
    pattern_name: Optional[str] = None
    pattern_type: Optional[str] = None
    detection_rules: Optional[Dict[str, Any]] = None
    confidence_threshold: Optional[float] = None

    # Emotion intelligence metrics
    emotion_signatures: Optional[Dict[str, Any]] = None
    early_warning_indicators: Optional[List[str]] = None

    # Efficacy tracking
    success_rate: Optional[float] = None
    false_positive_rate: Optional[float] = None
    avg_detection_week: Optional[float] = None

    # Risk assessment
    business_impact: Optional[str] = None
    student_impact: Optional[str] = None
    typical_outcome: Optional[str] = None

    # Intervention efficacy
    recommended_interventions: Optional[Dict[str, Any]] = None
    avg_intervention_efficacy: Optional[float] = None

    description: Optional[str] = None

class HistoricalPatternInDB(HistoricalPatternBase):
    id: uuid.UUID
    confidence_threshold: Optional[float] = None

    # Emotion intelligence metrics
    emotion_signatures: Optional[Dict[str, Any]] = None
    early_warning_indicators: Optional[List[str]] = None

    # Efficacy tracking
    success_rate: Optional[float] = None
    false_positive_rate: Optional[float] = None
    avg_detection_week: Optional[float] = None

    # Risk assessment
    business_impact: Optional[str] = None
    student_impact: Optional[str] = None
    typical_outcome: Optional[str] = None

    # Intervention efficacy
    recommended_interventions: Optional[Dict[str, Any]] = None
    avg_intervention_efficacy: Optional[float] = None

    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# New models for vector database integration
class EmotionPatternMatch(BaseModel):
    """Model for emotion pattern matches from vector database"""
    matched_student_id: str
    similarity_score: float
    emotion_profile: EmotionProfile
    match_timestamp: datetime = Field(default_factory=datetime.now)
    match_metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_langchain_document(
        cls, document: Document, similarity_score: float) -> 'EmotionPatternMatch':
        """Create an EmotionPatternMatch from a LangChain Document"""
        try:
            # Extract emotion profile from document content
            import json
            emotion_data = json.loads(document.page_content)
            emotion_profile = EmotionProfile.parse_obj(emotion_data)

            # Extract student ID from metadata
            student_id = document.metadata.get("student_id", "unknown")

            return cls(
                matched_student_id=student_id,
                similarity_score=similarity_score,
                emotion_profile=emotion_profile,
                match_metadata=document.metadata
            )
        except Exception as e:
            # Handle parsing errors
            raise ValueError(f"Failed to create EmotionPatternMatch from document: {e}")

    def to_langchain_document(self) -> Document:
        """Convert to a LangChain Document for storage"""
        import json

        # Convert emotion profile to JSON string
        content = json.dumps(self.emotion_profile.dict())

        # Prepare metadata
        metadata = self.match_metadata or {}
        metadata["student_id"] = self.matched_student_id
        metadata["similarity_score"] = self.similarity_score
        metadata["match_timestamp"] = self.match_timestamp.isoformat()

        return Document(
            page_content=content,
            metadata=metadata
        )

# Updated HistoricalPattern model for vector database integration
class HistoricalPattern(BaseModel):
    """Model for historical pattern analysis results"""
    student_id: str
    course_id: str
    week_number: int
    emotion_pattern_matches: List[EmotionPatternMatch] = []
    successful_interventions: List[Dict[str, Any]] = []
    emotion_recovery_probability: float = 0.0
    optimal_intervention_timing: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_langchain_documents(cls, student_id: str, course_id: str, week_number: int,
                               documents: List[Document], scores: List[float]) -> 'HistoricalPattern':
        """Create a HistoricalPattern from LangChain Documents with similarity scores"""
        # Create pattern matches from documents
        pattern_matches = []
        for doc, score in zip(documents, scores):
            try:
                match = EmotionPatternMatch.from_langchain_document(doc, score)
                pattern_matches.append(match)
            except Exception as e:
                print(f"Error creating pattern match: {e}")

        # Create the historical pattern
        return cls(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            emotion_pattern_matches=pattern_matches
        )

    def to_langchain_documents(self) -> List[Document]:
        """Convert to a list of LangChain Documents for storage"""
        documents = []

        # Convert each pattern match to a document
        for match in self.emotion_pattern_matches:
            try:
                doc = match.to_langchain_document()
                # Add additional metadata
                doc.metadata["course_id"] = self.course_id
                doc.metadata["week_number"] = self.week_number
                doc.metadata["recovery_probability"] = self.emotion_recovery_probability
                documents.append(doc)
            except Exception as e:
                print(f"Error converting pattern match to document: {e}")

        return documents
