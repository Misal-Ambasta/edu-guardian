from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class EmotionTrajectoryPrediction(BaseModel):
    """
    Model for emotion trajectory predictions including multi-week forecasts,
    risk escalations, and optimal intervention windows
    """
    emotion_predictions: Dict[str, Dict[str, float]]
    risk_escalations: Dict[str, Dict[str, Any]]
    optimal_intervention_windows: Dict[str, Dict[str, Any]]
    confidence_scores: Dict[str, float]

class StudentEmotionHistory(BaseModel):
    """
    Model for student emotion history used for trajectory predictions
    """
    student_id: str
    course_id: str
    weeks: List[int]
    frustration_levels: List[float]
    engagement_levels: List[float]
    confidence_levels: List[float]
    satisfaction_levels: List[float]
    emotional_trajectories: List[str]
    hidden_dissatisfaction_flags: List[bool]
    urgency_levels: List[str]
    emotional_temperatures: List[float]
    emotional_volatilities: List[float]
    metadata: Optional[Dict[str, Any]] = None
