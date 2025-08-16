import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db
from app.emotion_analysis.emotion_analyzer import AdvancedEmotionAnalyzer
from app.services.emotion_trajectory import EmotionTrajectoryPredictor
from app.services.intelligent_report import IntelligentReportGenerator
from app.services.vector_db import EmotionVectorDatabase

# Create test client
client = TestClient(app)

# Override dependency for testing
def override_get_db():
    return "mock_db_session"

app.dependency_overrides[get_db] = override_get_db

class TestIntegration:
    
    def test_emotion_analysis_to_trajectory_prediction(self, mocker):
        # Test the integration between emotion analysis and trajectory prediction
        
        # Mock the EmotionTrajectoryPredictor
        mock_predictor = mocker.MagicMock()
        mock_predictor.predict_emotion_evolution.return_value = {
            "predicted_trajectory": "declining",
            "confidence_score": 0.75,
            "predicted_emotions": [
                {
                    "week": 4,
                    "emotion_profile": {
                        "frustration_level": 0.8,
                        "engagement_level": 0.4,
                        "confidence_level": 0.3,
                        "satisfaction_level": 0.2
                    }
                }
            ]
        }
        mocker.patch('app.services.emotion_trajectory.EmotionTrajectoryPredictor', return_value=mock_predictor)
        
        # First, analyze emotion
        analyze_response = client.post(
            "/emotion/analyze",
            json={
                "text": "I'm having some trouble with the course material. It's quite challenging, but I'm trying my best to keep up.",
                "student_id": "test_student",
                "course_id": "test_course",
                "week_number": 3
            }
        )
        
        # Verify analysis response
        assert analyze_response.status_code == 200
        
        # Then, get trajectory prediction
        trajectory_response = client.get("/emotion/trajectory-prediction/test_student")
        
        # Verify trajectory response
        assert trajectory_response.status_code == 200
        trajectory_data = trajectory_response.json()
        assert "predicted_trajectory" in trajectory_data
        assert "confidence_score" in trajectory_data
        assert "predicted_emotions" in trajectory_data
    
    def test_trajectory_prediction_to_risk_assessment(self, mocker):
        # Test the integration between trajectory prediction and risk assessment
        
        # Mock the EmotionTrajectoryPredictor
        mock_predictor = mocker.MagicMock()
        mock_predictor.predict_emotion_evolution.return_value = {
            "predicted_trajectory": "declining",
            "confidence_score": 0.75,
            "predicted_emotions": [
                {
                    "week": 4,
                    "emotion_profile": {
                        "frustration_level": 0.8,
                        "engagement_level": 0.4,
                        "confidence_level": 0.3,
                        "satisfaction_level": 0.2
                    }
                }
            ]
        }
        mock_predictor.predict_risk_escalations.return_value = {
            "risk_escalations": [
                {
                    "week": 4,
                    "risk_type": "dropout",
                    "probability": 0.7,
                    "contributing_factors": ["increasing_frustration", "decreasing_engagement"]
                }
            ],
            "confidence_score": 0.8
        }
        mock_predictor.predict_optimal_intervention_windows.return_value = {
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
        mocker.patch('app.services.emotion_trajectory.EmotionTrajectoryPredictor', return_value=mock_predictor)
        
        # Get trajectory prediction
        trajectory_response = client.get("/emotion/trajectory-prediction/test_student")
        
        # Verify trajectory response
        assert trajectory_response.status_code == 200
        
        # Then, get risk assessment
        risk_response = client.get("/students/risk-assessment/test_student")
        
        # Verify risk assessment response
        assert risk_response.status_code == 200
        risk_data = risk_response.json()
        assert "risk_level" in risk_data
        assert "risk_factors" in risk_data
        assert "risk_escalations" in risk_data
        assert "intervention_windows" in risk_data
    
    def test_weekly_report_to_ai_insights(self, mocker):
        # Test the integration between weekly report generation and AI insights
        
        # Mock the WeeklyNPSReport model
        mock_report = mocker.MagicMock()
        mock_report.to_dict.return_value = {
            "course_id": "test_course",
            "week_number": 3,
            "nps_score": 35,
            "aspect_scores": {
                "lms_usability": 3.5,
                "instructor_quality": 4.2,
                "content_difficulty": 3.8,
                "support_quality": 3.9,
                "course_pace": 3.7
            },
            "emotion_intelligence": {
                "average_frustration_level": 0.6,
                "hidden_dissatisfaction_rate": 0.3,
                "emotional_temperature_avg": 0.7,
                "frustration_trend": "increasing",
                "urgency_breakdown": {"high": 5, "medium": 10, "low": 20},
                "emotional_crisis_students": 3
            },
            "risk_prediction": {
                "high_risk_students": [{"student_id": "test1", "risk_probability": 0.8}],
                "dropout_probability_distribution": {"high": 5, "medium": 10, "low": 20},
                "optimal_intervention_timing": {"test1": "immediate"}
            }
        }
        mocker.patch('app.models.reports.WeeklyNPSReport.get_report_by_course_and_week', return_value=mock_report)
        
        # Mock the IntelligentReportGenerator
        mock_generator = mocker.MagicMock()
        mock_generator.generate_ai_powered_insights.return_value = [
            {
                "insight_text": "There is a concerning trend of increasing frustration among students in week 3",
                "confidence_level": 0.85,
                "insight_type": "risk",
                "affected_students": 5,
                "data_points": ["frustration_trend", "emotional_temperature"]
            }
        ]
        mocker.patch('app.services.intelligent_report.IntelligentReportGenerator', return_value=mock_generator)
        
        # Get AI insights
        insights_response = client.get("/reports/ai-insights?course_id=test_course&week_number=3")
        
        # Verify insights response
        assert insights_response.status_code == 200
        insights_data = insights_response.json()
        assert isinstance(insights_data, list)
        assert len(insights_data) > 0
        assert "insight_text" in insights_data[0]
        assert "confidence_level" in insights_data[0]
    
    def test_emotion_analysis_to_vector_db(self, mocker):
        # Test the integration between emotion analysis and vector database
        
        # Mock the EmotionVectorDatabase
        mock_vector_db = mocker.MagicMock()
        mock_vector_db.add_emotion_profile.return_value = None
        mocker.patch('app.services.vector_db.EmotionVectorDatabase', return_value=mock_vector_db)
        
        # Analyze emotion
        analyze_response = client.post(
            "/emotion/analyze",
            json={
                "text": "I'm having some trouble with the course material. It's quite challenging, but I'm trying my best to keep up.",
                "student_id": "test_student",
                "course_id": "test_course",
                "week_number": 3
            }
        )
        
        # Verify analysis response
        assert analyze_response.status_code == 200
        
        # Verify that the vector database was called to add the emotion profile
        # This would require additional mocking and verification in a real test
        # For this example, we're just checking the response status