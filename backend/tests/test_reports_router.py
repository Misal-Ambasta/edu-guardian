import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db
from app.services.intelligent_report import IntelligentReportGenerator
from app.models.reports import WeeklyNPSReport

# Create test client
client = TestClient(app)

# Mock data and services
class MockIntelligentReportGenerator:
    def __init__(self, db_session):
        pass
    
    def generate_ai_powered_insights(self, report_data):
        return [
            {
                "insight_text": "There is a concerning trend of increasing frustration among students in week 3",
                "confidence_level": 0.85,
                "insight_type": "risk",
                "affected_students": 5,
                "data_points": ["frustration_trend", "emotional_temperature"]
            },
            {
                "insight_text": "Students are responding positively to the recent UI improvements in the LMS",
                "confidence_level": 0.78,
                "insight_type": "positive",
                "affected_students": 12,
                "data_points": ["lms_usability", "satisfaction_level"]
            }
        ]
    
    def generate_dynamic_recommendations(self, insights):
        return [
            {
                "recommendation_text": "Schedule additional technical support sessions to address the increasing frustration",
                "priority": "high",
                "expected_impact": 0.7,
                "target_audience": "students with technical issues",
                "implementation_difficulty": "medium"
            },
            {
                "recommendation_text": "Continue with the planned UI improvements based on positive student feedback",
                "priority": "medium",
                "expected_impact": 0.6,
                "target_audience": "all students",
                "implementation_difficulty": "low"
            }
        ]

class MockWeeklyNPSReport:
    @staticmethod
    def get_report_by_course_and_week(db, course_id, week_number):
        if course_id == "test_course" and week_number == 3:
            return MockWeeklyNPSReport()
        return None
    
    def to_dict(self):
        return {
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
            },
            "executive_summary": "This is a test executive summary for week 3 of test_course.",
            "report_confidence": 0.85,
            "data_quality_score": 0.9
        }

# Override dependency
def override_get_db():
    return "mock_db_session"

def override_intelligent_report_generator(db):
    return MockIntelligentReportGenerator(db)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[IntelligentReportGenerator] = override_intelligent_report_generator

# Mock the WeeklyNPSReport model
app.dependency_overrides[WeeklyNPSReport] = MockWeeklyNPSReport

class TestReportsRouter:
    
    def test_ai_insights_endpoint(self, monkeypatch):
        # Mock the WeeklyNPSReport.get_report_by_course_and_week method
        monkeypatch.setattr(WeeklyNPSReport, "get_report_by_course_and_week", MockWeeklyNPSReport.get_report_by_course_and_week)
        
        # Test the AI insights endpoint
        response = client.get("/reports/ai-insights?course_id=test_course&week_number=3")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "insight_text" in data[0]
        assert "confidence_level" in data[0]
    
    def test_recommendations_endpoint(self, monkeypatch):
        # Mock the WeeklyNPSReport.get_report_by_course_and_week method
        monkeypatch.setattr(WeeklyNPSReport, "get_report_by_course_and_week", MockWeeklyNPSReport.get_report_by_course_and_week)
        
        # Test the recommendations endpoint
        response = client.get("/reports/recommendations?course_id=test_course&week_number=3")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "recommendation_text" in data[0]
        assert "priority" in data[0]
    
    def test_executive_summary_endpoint(self, monkeypatch):
        # Mock the WeeklyNPSReport.get_report_by_course_and_week method
        monkeypatch.setattr(WeeklyNPSReport, "get_report_by_course_and_week", MockWeeklyNPSReport.get_report_by_course_and_week)
        
        # Test the executive summary endpoint
        response = client.get("/reports/executive-summary?course_id=test_course&week_number=3")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "executive_summary" in data
        assert "report_confidence" in data
        assert "data_quality_score" in data
    
    def test_report_not_found(self, monkeypatch):
        # Mock the WeeklyNPSReport.get_report_by_course_and_week method
        monkeypatch.setattr(WeeklyNPSReport, "get_report_by_course_and_week", MockWeeklyNPSReport.get_report_by_course_and_week)
        
        # Test with non-existent report
        response = client.get("/reports/ai-insights?course_id=nonexistent&week_number=1")
        
        # Verify response
        assert response.status_code == 404