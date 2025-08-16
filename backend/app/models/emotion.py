from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class EmotionProfile(BaseModel):
    """Model representing a student's emotion profile based on analysis of their text."""
    primary_emotion: str = Field(..., description="The primary emotion detected")
    emotion_scores: Dict[str, float] = Field(..., description="Dictionary of emotion scores")
    sentiment_score: float = Field(..., description="Overall sentiment score from -1 to 1")
    confidence: float = Field(..., description="Confidence level in the emotion analysis")
    timestamp: Optional[str] = Field(None, description="Timestamp when the emotion was analyzed")
    text_sample: Optional[str] = Field(None, description="Sample of text that was analyzed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the analysis")