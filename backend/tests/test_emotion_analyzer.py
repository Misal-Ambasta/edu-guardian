import pytest
from app.emotion_analysis.analyzer import AdvancedEmotionAnalyzer
from app.models.student_journey import EmotionProfile

class TestAdvancedEmotionAnalyzer:
    
    def setup_method(self):
        self.analyzer = AdvancedEmotionAnalyzer()
    
    def test_analyze_text_returns_emotion_profile(self):
        # Test that analyze_text returns an EmotionProfile
        text = "The course is good but the LMS is confusing and frustrating to use."
        result = self.analyzer.analyze_text(text)
        assert isinstance(result, EmotionProfile)
    
    def test_frustration_detection(self):
        # Test frustration detection
        text = "I'm extremely frustrated with the LMS, it's very difficult to navigate."
        result = self.analyzer.analyze_text(text)
        assert result.frustration_level > 0.7
        assert result.frustration_type == "technical"
    
    def test_hidden_dissatisfaction_detection(self):
        # Test hidden dissatisfaction detection
        text = "The instructor is fine, I guess. The course is okay."
        result = self.analyzer.analyze_text(text)
        assert result.hidden_dissatisfaction_flag == True
        assert result.hidden_dissatisfaction_confidence > 0.6
    
    def test_urgency_detection(self):
        # Test urgency detection
        text = "I need help immediately! I'm considering dropping the course if this isn't fixed soon."
        result = self.analyzer.analyze_text(text)
        assert result.urgency_level in ["high", "critical", "immediate"]
        assert "considering_dropping" in result.urgency_signals
    
    def test_emotional_temperature_calculation(self):
        # Test emotional temperature calculation
        text = "I am absolutely furious about the lack of support and terrible course materials!"
        result = self.analyzer.analyze_text(text)
        assert result.emotional_temperature > 0.8
        assert result.emotional_volatility > 0.7
    
    def test_positive_emotion_detection(self):
        # Test positive emotion detection
        text = "I'm really enjoying the course and feel confident about my progress."
        result = self.analyzer.analyze_text(text)
        assert result.satisfaction_level > 0.8
        assert result.confidence_level > 0.7
        assert result.frustration_level < 0.3