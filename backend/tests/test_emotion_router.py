import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db
from app.models.student_journey import EmotionProfile
from app.services.emotion_trajectory import EmotionTrajectoryPredictor
import json

# Create test client
client = TestClient(app)

# Mock data and services
class MockEmotionTrajectoryPredictor:
    def get_student_emotion_history(self, student_id):
        return [
            {
                "week": 1,
                "emotion_profile": EmotionProfile(
                    frustration_level=0.3,
                    engagement_level=0.8,
                    confidence_level=0.7,
                    satisfaction_level=0.6,
                    frustration_type="content",
                    frustration_intensity="mild",
                    frustration_trend="stable",
                    urgency_level="low",
                    urgency_signals=[],
                    response_urgency="routine",
                    emotional_temperature=0.4,
                    emotional_volatility=0.2,
                    emotional_trajectory="stable",
                    hidden_dissatisfaction_flag=False,
                    hidden_dissatisfaction_confidence=0.1,
                    hidden_signals=[],
                    politeness_mask_level=0.3,
                    dropout_risk_emotions=[],
                    positive_recovery_indicators=["enthusiasm"],
                    emotional_triggers=[],
                    emotion_coherence=0.8,
                    sentiment_authenticity=0.9,
                    emotional_complexity="simple"
                )
            },
            {
                "week": 2,
                "emotion_profile": EmotionProfile(
                    frustration_level=0.5,
                    engagement_level=0.7,
                    confidence_level=0.6,
                    satisfaction_level=0.5,
                    frustration_type="technical",
                    frustration_intensity="moderate",
                    frustration_trend="increasing",
                    urgency_level="medium",
                    urgency_signals=["help_requests"],
                    response_urgency="this_week",
                    emotional_temperature=0.5,
                    emotional_volatility=0.3,
                    emotional_trajectory="declining",
                    hidden_dissatisfaction_flag=True,
                    hidden_dissatisfaction_confidence=0.6,
                    hidden_signals=["diplomatic_language"],
                    politeness_mask_level=0.5,
                    dropout_risk_emotions=["frustration"],
                    positive_recovery_indicators=[],
                    emotional_triggers=["technical_issues"],
                    emotion_coherence=0.7,
                    sentiment_authenticity=0.7,
                    emotional_complexity="moderate"
                )
            }
        ]
    
    def predict_emotion_evolution(self, emotion_history):
        return {
            "predicted_trajectory": "declining",
            "confidence_score": 0.75,
            "predicted_emotions": [
                {
                    "week": 3,
                    "emotion_profile": {
                        "frustration_level": 0.7,
                        "engagement_level": 0.5,
                        "confidence_level": 0.4,
                        "satisfaction_level": 0.3,
                        "frustration_type": "technical",
                        "frustration_intensity": "high",
                        "frustration_trend": "increasing",
                        "urgency_level": "high",
                        "emotional_temperature": 0.7,
                        "emotional_trajectory": "declining",
                        "hidden_dissatisfaction_flag": True
                    }
                }
            ]
        }
    
    def predict_multi_week_emotions(self, emotion_history, weeks_ahead):
        return {
            "predictions": [
                {
                    "week": 3,
                    "emotion_profile": {
                        "frustration_level": 0.7,
                        "engagement_level": 0.5,
                        "confidence_level": 0.4,
                        "satisfaction_level": 0.3
                    }
                },
                {
                    "week": 4,
                    "emotion_profile": {
                        "frustration_level": 0.8,
                        "engagement_level": 0.4,
                        "confidence_level": 0.3,
                        "satisfaction_level": 0.2
                    }
                }
            ],
            "confidence_score": 0.7
        }
    
    def predict_risk_escalations(self, emotion_history):
        return {
            "risk_escalations": [
                {
                    "week": 3,
                    "risk_type": "dropout",
                    "probability": 0.6,
                    "contributing_factors": ["increasing_frustration", "decreasing_engagement"]
                }
            ],
            "confidence_score": 0.7
        }
    
    def predict_optimal_intervention_windows(self, emotion_history):
        return {
            "intervention_windows": [
                {
                    "window_start": "week_3",
                    "window_end": "week_4",
                    "intervention_type": "technical_support",
                    "urgency": "high",
                    "effectiveness_probability": 0.8
                }
            ],
            "confidence_score": 0.75
        }

# Override dependency
def override_get_db():
    return "mock_db_session"

def override_emotion_trajectory_predictor(db):
    return MockEmotionTrajectoryPredictor()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[EmotionTrajectoryPredictor] = override_emotion_trajectory_predictor

class TestEmotionRouter:
    
    def test_trajectory_prediction_endpoint(self):
        # Test the trajectory prediction endpoint
        response = client.get("/emotion/trajectory-prediction/student123")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "predicted_trajectory" in data
        assert "confidence_score" in data
        assert "predicted_emotions" in data
        assert len(data["predicted_emotions"]) > 0
    
    def test_multi_week_prediction_endpoint(self):
        # Test the multi-week prediction endpoint
        response = client.get("/emotion/multi-week-prediction/student123?weeks_ahead=2")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "confidence_score" in data
        assert len(data["predictions"]) > 0
    
    def test_risk_escalation_endpoint(self):
        # Test the risk escalation endpoint
        response = client.get("/emotion/risk-escalation/student123")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "risk_escalations" in data
        assert "confidence_score" in data
        assert len(data["risk_escalations"]) > 0
    
    def test_intervention_window_endpoint(self):
        # Test the intervention window endpoint
        response = client.get("/emotion/intervention-window/student123")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "intervention_windows" in data
        assert "confidence_score" in data
        assert len(data["intervention_windows"]) > 0