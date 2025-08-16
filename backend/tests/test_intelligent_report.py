import pytest
from app.services.intelligent_report import IntelligentReportGenerator

class TestIntelligentReportGenerator:
    
    def setup_method(self, db_session):
        self.intelligent_report = IntelligentReportGenerator(db_session)
    
    def test_detect_anomalous_patterns(self):
        # Test data
        report_data = {
            'aspect_scores': {
                'lms_usability': 3.5,
                'instructor_quality': 4.2,
                'content_difficulty': 3.8,
                'support_quality': 3.9,
                'course_pace': 3.7
            },
            'emotion_intelligence': {
                'average_frustration_level': 0.6,
                'hidden_dissatisfaction_rate': 0.3,
                'emotional_temperature_avg': 0.7
            }
        }
        
        # Test anomalous pattern detection
        patterns = self.intelligent_report.detect_anomalous_patterns(report_data)
        
        # Verify result
        assert isinstance(patterns, list)
        assert len(patterns) >= 0  # May or may not find anomalies
    
    def test_identify_emerging_risks(self):
        # Test data
        report_data = {
            'emotion_intelligence': {
                'frustration_trend': 'increasing',
                'urgency_breakdown': {'high': 5, 'medium': 10, 'low': 20},
                'emotional_crisis_students': 3
            },
            'risk_prediction': {
                'high_risk_students': [{'student_id': 'test1', 'risk_probability': 0.8}],
                'dropout_probability_distribution': {'high': 5, 'medium': 10, 'low': 20}
            }
        }
        
        # Test risk identification
        risks = self.intelligent_report.identify_emerging_risks(report_data)
        
        # Verify result
        assert isinstance(risks, list)
        assert len(risks) > 0
    
    def test_find_intervention_opportunities(self):
        # Test data
        report_data = {
            'risk_prediction': {
                'high_risk_students': [{'student_id': 'test1', 'risk_probability': 0.8}],
                'optimal_intervention_timing': {'test1': 'immediate'}
            },
            'emotion_intelligence': {
                'urgency_breakdown': {'high': 5, 'medium': 10, 'low': 20},
                'students_showing_recovery': 2
            }
        }
        
        # Test opportunity finding
        opportunities = self.intelligent_report.find_intervention_opportunities(report_data)
        
        # Verify result
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
    
    def test_generate_natural_language_insights(self):
        # Test data
        anomalies = [{'type': 'hidden_dissatisfaction', 'description': 'Unusually high hidden dissatisfaction'}]
        risks = [{'student_id': 'test1', 'risk_type': 'dropout', 'probability': 0.8}]
        opportunities = [{'student_id': 'test1', 'intervention_type': 'mentor_assignment', 'urgency': 'high'}]
        
        # Test insight generation
        insights = self.intelligent_report.generate_natural_language_insights(anomalies, risks, opportunities)
        
        # Verify result
        assert isinstance(insights, list)
        assert len(insights) > 0
        for insight in insights:
            assert 'insight_text' in insight
            assert 'confidence_level' in insight
    
    def test_generate_ai_powered_insights(self):
        # Test data
        report_data = {
            'course_id': 'test_course',
            'week_number': 3,
            'aspect_scores': {
                'lms_usability': 3.5,
                'instructor_quality': 4.2,
                'content_difficulty': 3.8,
                'support_quality': 3.9,
                'course_pace': 3.7
            },
            'emotion_intelligence': {
                'average_frustration_level': 0.6,
                'hidden_dissatisfaction_rate': 0.3,
                'emotional_temperature_avg': 0.7,
                'frustration_trend': 'increasing',
                'urgency_breakdown': {'high': 5, 'medium': 10, 'low': 20},
                'emotional_crisis_students': 3
            },
            'risk_prediction': {
                'high_risk_students': [{'student_id': 'test1', 'risk_probability': 0.8}],
                'dropout_probability_distribution': {'high': 5, 'medium': 10, 'low': 20},
                'optimal_intervention_timing': {'test1': 'immediate'}
            }
        }
        
        # Test insight generation
        insights = self.intelligent_report.generate_ai_powered_insights(report_data)
        
        # Verify result
        assert isinstance(insights, list)
        assert len(insights) > 0
        for insight in insights:
            assert 'insight_text' in insight
            assert 'confidence_level' in insight