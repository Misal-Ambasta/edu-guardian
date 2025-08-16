import pytest
from app.emotion_analysis.emotion_analyzer import AdvancedEmotionAnalyzer
from app.services.emotion_trajectory import EmotionTrajectoryPredictor
from app.models.student_journey import EmotionProfile

class TestAccuracy:
    
    def setup_method(self):
        self.emotion_analyzer = AdvancedEmotionAnalyzer()
    
    def test_emotion_analyzer_accuracy(self):
        # Test cases with expected emotion profiles
        test_cases = [
            {
                "text": "I'm really struggling with this course. The material is confusing and I can't get help when I need it.",
                "expected": {
                    "frustration_level": (0.7, 0.9),  # Range of acceptable values
                    "hidden_dissatisfaction_flag": True,
                    "urgency_level": "high"
                }
            },
            {
                "text": "The course is going well. I'm enjoying the material and finding it challenging but manageable.",
                "expected": {
                    "frustration_level": (0.0, 0.3),
                    "hidden_dissatisfaction_flag": False,
                    "urgency_level": "low"
                }
            },
            {
                "text": "The assignments are taking longer than I expected, but I'm making progress. The instructor's explanations could be clearer though.",
                "expected": {
                    "frustration_level": (0.3, 0.6),
                    "hidden_dissatisfaction_flag": True,
                    "urgency_level": "medium"
                }
            }
        ]
        
        # Test each case
        for case in test_cases:
            result = self.emotion_analyzer.analyze_text(case["text"])
            
            # Check that the results fall within expected ranges
            for key, expected_value in case["expected"].items():
                if isinstance(expected_value, tuple):
                    # For numeric ranges
                    assert expected_value[0] <= getattr(result, key) <= expected_value[1], \
                        f"Expected {key} between {expected_value[0]} and {expected_value[1]}, got {getattr(result, key)}"
                else:
                    # For exact matches
                    assert getattr(result, key) == expected_value, \
                        f"Expected {key} to be {expected_value}, got {getattr(result, key)}"
    
    def test_hidden_dissatisfaction_detection_accuracy(self):
        # Test cases specifically for hidden dissatisfaction
        test_cases = [
            {
                "text": "The course is fine I guess. The materials are somewhat helpful.",
                "expected_flag": True,
                "expected_confidence": (0.6, 1.0)
            },
            {
                "text": "I appreciate the instructor's efforts, but I'm still confused about the key concepts.",
                "expected_flag": True,
                "expected_confidence": (0.7, 1.0)
            },
            {
                "text": "I'm absolutely loving this course! The material is fascinating and the instructor is excellent.",
                "expected_flag": False,
                "expected_confidence": (0.0, 0.3)
            }
        ]
        
        # Test each case
        for case in test_cases:
            result = self.emotion_analyzer.analyze_text(case["text"])
            
            # Check hidden dissatisfaction flag
            assert result.hidden_dissatisfaction_flag == case["expected_flag"], \
                f"Expected hidden_dissatisfaction_flag to be {case['expected_flag']}, got {result.hidden_dissatisfaction_flag}"
            
            # Check confidence level is in expected range
            min_conf, max_conf = case["expected_confidence"]
            assert min_conf <= result.hidden_dissatisfaction_confidence <= max_conf, \
                f"Expected hidden_dissatisfaction_confidence between {min_conf} and {max_conf}, got {result.hidden_dissatisfaction_confidence}"
    
    def test_trajectory_prediction_accuracy(self, mocker):
        # Mock the database session and student emotion history
        mock_db = mocker.MagicMock()
        trajectory_predictor = EmotionTrajectoryPredictor(mock_db)
        
        # Create a mock emotion history with a clear trend
        emotion_history = [
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
            },
            {
                "week": 3,
                "emotion_profile": EmotionProfile(
                    frustration_level=0.7,
                    engagement_level=0.5,
                    confidence_level=0.4,
                    satisfaction_level=0.3,
                    frustration_type="technical",
                    frustration_intensity="high",
                    frustration_trend="increasing",
                    urgency_level="high",
                    urgency_signals=["missed_deadlines", "help_requests"],
                    response_urgency="immediate",
                    emotional_temperature=0.7,
                    emotional_volatility=0.6,
                    emotional_trajectory="declining",
                    hidden_dissatisfaction_flag=True,
                    hidden_dissatisfaction_confidence=0.8,
                    hidden_signals=["diplomatic_language", "faint_praise"],
                    politeness_mask_level=0.7,
                    dropout_risk_emotions=["frustration", "helplessness"],
                    positive_recovery_indicators=[],
                    emotional_triggers=["technical_issues", "deadline_pressure"],
                    emotion_coherence=0.5,
                    sentiment_authenticity=0.5,
                    emotional_complexity="complex"
                )
            }
        ]
        
        # Mock the get_student_emotion_history method
        mocker.patch.object(
            trajectory_predictor,
            'get_student_emotion_history',
            return_value=emotion_history
        )
        
        # Test prediction
        prediction = trajectory_predictor.predict_emotion_evolution(emotion_history)
        
        # Verify prediction accuracy
        assert prediction["predicted_trajectory"] == "declining", \
            f"Expected predicted_trajectory to be 'declining', got {prediction['predicted_trajectory']}"
        
        # Verify confidence score is reasonable
        assert 0.7 <= prediction["confidence_score"] <= 1.0, \
            f"Expected confidence_score between 0.7 and 1.0, got {prediction['confidence_score']}"
        
        # Verify predicted emotions show continued decline
        predicted_week = prediction["predicted_emotions"][0]
        assert predicted_week["week"] == 4  # Next week
        
        # Verify frustration continues to increase
        assert predicted_week["emotion_profile"]["frustration_level"] >= 0.7, \
            f"Expected frustration_level >= 0.7, got {predicted_week['emotion_profile']['frustration_level']}"
        
        # Verify engagement continues to decrease
        assert predicted_week["emotion_profile"]["engagement_level"] <= 0.5, \
            f"Expected engagement_level <= 0.5, got {predicted_week['emotion_profile']['engagement_level']}"