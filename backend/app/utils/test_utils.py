"""Utility functions for the application.
"""

from app.models.emotion import EmotionProfile

def create_test_emotion_profile():
    """Create a test emotion profile for testing purposes."""
    return EmotionProfile(
        frustration_level=0.7,
        engagement_level=0.4,
        confidence_level=0.3,
        satisfaction_level=0.2,
        emotional_temperature=0.8,
        emotional_volatility=0.6,
        hidden_dissatisfaction_flag=True,
        urgency_level="high",
        frustration_type="technical",
        emotional_trajectory="declining",
        dominant_emotions=["frustration", "anxiety"],
        sentiment_score=-0.6
    )
