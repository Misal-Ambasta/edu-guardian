import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db
from app.models.student_journey import EmotionProfile
from app.emotion_analysis.emotion_analyzer import AdvancedEmotionAnalyzer
from app.services.emotion_trajectory import EmotionTrajectoryPredictor
from app.services.intelligent_report import IntelligentReportGenerator
from jsonschema import validate

# Create test client
client = TestClient(app)

# Override dependency for testing
def override_get_db():
    return "mock_db_session"

app.dependency_overrides[get_db] = override_get_db

class TestValidation:
    
    def test_emotion_profile_schema_validation(self):
        # Define the expected schema for EmotionProfile
        emotion_profile_schema = {
            "type": "object",
            "properties": {
                "frustration_level": {"type": "number", "minimum": 0, "maximum": 1},
                "engagement_level": {"type": "number", "minimum": 0, "maximum": 1},
                "confidence_level": {"type": "number", "minimum": 0, "maximum": 1},
                "satisfaction_level": {"type": "number", "minimum": 0, "maximum": 1},
                "frustration_type": {"type": "string"},
                "frustration_intensity": {"type": "string"},
                "frustration_trend": {"type": "string"},
                "urgency_level": {"type": "string"},
                "urgency_signals": {"type": "array", "items": {"type": "string"}},
                "response_urgency": {"type": "string"},
                "emotional_temperature": {"type": "number", "minimum": 0, "maximum": 1},
                "emotional_volatility": {"type": "number", "minimum": 0, "maximum": 1},
                "emotional_trajectory": {"type": "string"},
                "hidden_dissatisfaction_flag": {"type": "boolean"},
                "hidden_dissatisfaction_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "hidden_signals": {"type": "array", "items": {"type": "string"}},
                "politeness_mask_level": {"type": "number", "minimum": 0, "maximum": 1},
                "dropout_risk_emotions": {"type": "array", "items": {"type": "string"}},
                "positive_recovery_indicators": {"type": "array", "items": {"type": "string"}},
                "emotional_triggers": {"type": "array", "items": {"type": "string"}},
                "emotion_coherence": {"type": "number", "minimum": 0, "maximum": 1},
                "sentiment_authenticity": {"type": "number", "minimum": 0, "maximum": 1},
                "emotional_complexity": {"type": "string"}
            },
            "required": [
                "frustration_level", "engagement_level", "confidence_level", "satisfaction_level",
                "frustration_type", "frustration_intensity", "frustration_trend",
                "urgency_level", "urgency_signals", "response_urgency",
                "emotional_temperature", "emotional_volatility", "emotional_trajectory",
                "hidden_dissatisfaction_flag", "hidden_dissatisfaction_confidence", "hidden_signals",
                "politeness_mask_level", "dropout_risk_emotions", "positive_recovery_indicators",
                "emotional_triggers", "emotion_coherence", "sentiment_authenticity", "emotional_complexity"
            ]
        }
        
        # Create an instance of EmotionProfile
        emotion_profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.6,
            confidence_level=0.5,
            satisfaction_level=0.4,
            frustration_type="technical",
            frustration_intensity="moderate",
            frustration_trend="increasing",
            urgency_level="medium",
            urgency_signals=["missed_deadlines", "help_requests"],
            response_urgency="same_day",
            emotional_temperature=0.6,
            emotional_volatility=0.5,
            emotional_trajectory="declining",
            hidden_dissatisfaction_flag=True,
            hidden_dissatisfaction_confidence=0.8,
            hidden_signals=["faint_praise", "diplomatic_language"],
            politeness_mask_level=0.7,
            dropout_risk_emotions=["helplessness", "overwhelm"],
            positive_recovery_indicators=[],
            emotional_triggers=["technical_issues"],
            emotion_coherence=0.6,
            sentiment_authenticity=0.7,
            emotional_complexity="mixed"
        )
        
        # Convert to dict for validation
        emotion_profile_dict = emotion_profile.dict()
        
        # Validate against schema
        validate(instance=emotion_profile_dict, schema=emotion_profile_schema)
    
    def test_trajectory_prediction_response_validation(self):
        # Define the expected schema for trajectory prediction response
        trajectory_schema = {
            "type": "object",
            "properties": {
                "predicted_trajectory": {"type": "string"},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                "predicted_emotions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "week": {"type": "integer", "minimum": 1},
                            "emotion_profile": {"type": "object"}
                        },
                        "required": ["week", "emotion_profile"]
                    }
                }
            },
            "required": ["predicted_trajectory", "confidence_score", "predicted_emotions"]
        }
        
        # Make a request to the trajectory prediction endpoint
        response = client.get("/emotion/trajectory-prediction/test_student")
        
        # Verify response status
        assert response.status_code == 200
        
        # Validate response against schema
        validate(instance=response.json(), schema=trajectory_schema)
    
    def test_risk_assessment_response_validation(self):
        # Define the expected schema for risk assessment response
        risk_schema = {
            "type": "object",
            "properties": {
                "risk_level": {"type": "string"},
                "risk_factors": {"type": "array", "items": {"type": "string"}},
                "risk_escalations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "week": {"type": "integer", "minimum": 1},
                            "risk_type": {"type": "string"},
                            "probability": {"type": "number", "minimum": 0, "maximum": 1},
                            "contributing_factors": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["week", "risk_type", "probability"]
                    }
                },
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                "intervention_windows": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "window_start": {"type": "string"},
                            "window_end": {"type": "string"},
                            "intervention_type": {"type": "string"},
                            "urgency": {"type": "string"},
                            "effectiveness_probability": {"type": "number", "minimum": 0, "maximum": 1}
                        },
                        "required": ["window_start", "window_end", "intervention_type", "urgency"]
                    }
                }
            },
            "required": ["risk_level", "risk_factors", "risk_escalations", "confidence_score", "intervention_windows"]
        }
        
        # Make a request to the risk assessment endpoint
        response = client.get("/students/risk-assessment/test_student")
        
        # Verify response status
        assert response.status_code == 200
        
        # Validate response against schema
        validate(instance=response.json(), schema=risk_schema)
    
    def test_ai_insights_response_validation(self):
        # Define the expected schema for AI insights response
        insights_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "insight_text": {"type": "string"},
                    "confidence_level": {"type": "number", "minimum": 0, "maximum": 1},
                    "insight_type": {"type": "string"},
                    "affected_students": {"type": "integer", "minimum": 0},
                    "data_points": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["insight_text", "confidence_level"]
            }
        }
        
        # Make a request to the AI insights endpoint
        response = client.get("/reports/ai-insights?course_id=test_course&week_number=3")
        
        # If the response is successful, validate against schema
        if response.status_code == 200:
            validate(instance=response.json(), schema=insights_schema)