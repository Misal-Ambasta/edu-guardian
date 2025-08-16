import pytest
from datetime import datetime, timedelta
from app.services.trajectory_predictor import EmotionTrajectoryPredictor
from app.models.emotion_trajectory import EmotionTrajectoryPrediction, StudentEmotionHistory

class TestEmotionTrajectoryPredictor:
    
    def setup_method(self, db_session):
        self.predictor = EmotionTrajectoryPredictor(db_session)
        
        # Create mock student emotion history
        self.student_history = [
            StudentEmotionHistory(
                student_id="test_student_1",
                week_number=i,
                timestamp=datetime.now() - timedelta(days=(4-i)*7),
                frustration_level=0.5 + (i * 0.1),
                engagement_level=0.8 - (i * 0.05),
                confidence_level=0.7 - (i * 0.1),
                satisfaction_level=0.6 - (i * 0.1),
                emotional_temperature=0.4 + (i * 0.1),
                hidden_dissatisfaction_flag=(i > 2)
            ) for i in range(5)
        ]
    
    def test_predict_emotion_evolution(self, mocker):
        # Mock the get_student_emotion_history method
        mocker.patch.object(
            self.predictor, 'get_student_emotion_history', 
            return_value=self.student_history
        )
        
        # Test prediction
        result = self.predictor.predict_emotion_evolution("test_student_1")
        
        # Verify result
        assert isinstance(result, EmotionTrajectoryPrediction)
        assert result.student_id == "test_student_1"
        assert len(result.predicted_emotions) > 0
        assert result.confidence_score > 0
    
    def test_predict_next_week_emotions(self, mocker):
        # Mock the get_student_emotion_history method
        mocker.patch.object(
            self.predictor, 'get_student_emotion_history', 
            return_value=self.student_history
        )
        
        # Test prediction
        result = self.predictor.predict_next_week_emotions("test_student_1")
        
        # Verify result
        assert isinstance(result, EmotionTrajectoryPrediction)
        assert result.student_id == "test_student_1"
        assert len(result.predicted_emotions) == 1
        assert result.confidence_score > 0
    
    def test_predict_risk_escalations(self, mocker):
        # Mock the get_student_emotion_history method
        mocker.patch.object(
            self.predictor, 'get_student_emotion_history', 
            return_value=self.student_history
        )
        
        # Test prediction
        result = self.predictor.predict_risk_escalations("test_student_1")
        
        # Verify result
        assert isinstance(result, dict)
        assert "risk_points" in result
        assert "confidence_score" in result
        assert len(result["risk_points"]) > 0
    
    def test_predict_optimal_intervention_windows(self, mocker):
        # Mock the get_student_emotion_history method
        mocker.patch.object(
            self.predictor, 'get_student_emotion_history', 
            return_value=self.student_history
        )
        
        # Test prediction
        result = self.predictor.predict_optimal_intervention_windows("test_student_1")
        
        # Verify result
        assert isinstance(result, dict)
        assert "intervention_windows" in result
        assert "confidence_score" in result
        assert len(result["intervention_windows"]) > 0